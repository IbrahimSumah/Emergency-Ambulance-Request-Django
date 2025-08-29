from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, ParamedicProfileForm, ExtendedProfileForm
from .models import User, UserProfile
from ambulance.models import AmbulanceRequest


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect based on user role
                if user.is_admin_user():
                    return redirect('admin_dashboard')
                elif user.is_paramedic():
                    return redirect('paramedic_dashboard')
                else:
                    return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    
    # Add role-specific context
    if request.user.is_patient():
        context['recent_requests'] = AmbulanceRequest.objects.filter(
            patient=request.user
        ).order_by('-created_at')[:5]
    elif request.user.is_paramedic():
        context['assigned_requests'] = AmbulanceRequest.objects.filter(
            paramedic=request.user,
            status__in=['assigned', 'en_route', 'arrived']
        ).order_by('-created_at')[:5]
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = ExtendedProfileForm(request.POST, instance=profile)
        
        # Add paramedic form if user is paramedic
        paramedic_form = None
        if request.user.is_paramedic():
            paramedic_form = ParamedicProfileForm(request.POST, instance=request.user)
        
        forms_valid = user_form.is_valid() and profile_form.is_valid()
        if paramedic_form:
            forms_valid = forms_valid and paramedic_form.is_valid()
        
        if forms_valid:
            user_form.save()
            profile_form.save()
            if paramedic_form:
                paramedic_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ExtendedProfileForm(instance=profile)
        paramedic_form = ParamedicProfileForm(instance=request.user) if request.user.is_paramedic() else None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'paramedic_form': paramedic_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def toggle_availability(request):
    """Toggle paramedic availability (AJAX endpoint)"""
    if not request.user.is_paramedic():
        return JsonResponse({'error': 'Only paramedics can toggle availability'}, status=403)
    
    request.user.is_available = not request.user.is_available
    request.user.save()
    
    return JsonResponse({
        'success': True,
        'is_available': request.user.is_available,
        'status_text': 'Available' if request.user.is_available else 'Unavailable'
    })


def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.is_admin_user():
        return redirect('admin_dashboard')
    elif request.user.is_paramedic():
        return redirect('paramedic_dashboard')
    else:
        return redirect('patient_dashboard')
