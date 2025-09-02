from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.db import models
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, ParamedicProfileForm, ExtendedProfileForm, AdminUserEditForm, AdminParamedicEditForm
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
def manage_users_view(request):
    """Admin: Manage users list with basic filters"""
    if not request.user.is_admin_user():
        messages.error(request, 'Only admins can access Manage Users.')
        return redirect('accounts:dashboard_redirect')
    
    users = User.objects.all().order_by('-date_joined')
    role = request.GET.get('role')
    q = request.GET.get('q')
    if role in ['patient', 'paramedic', 'admin']:
        users = users.filter(role=role)
    if q:
        users = users.filter(models.Q(username__icontains=q) | models.Q(email__icontains=q))
    
    context = {
        'users': users,
        'role': role or '',
        'q': q or '',
        'total_users': User.objects.count(),
        'total_patients': User.objects.filter(role='patient').count(),
        'total_paramedics': User.objects.filter(role='paramedic').count(),
        'total_admins': User.objects.filter(role='admin').count(),
    }
    
    return render(request, 'accounts/manage_users.html', context)

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


@login_required
def admin_edit_user_view(request, user_id):
    """Admin: Edit user details"""
    if not request.user.is_admin_user():
        messages.error(request, 'Only admins can edit users.')
        return redirect('accounts:dashboard_redirect')
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Ensure user profile exists
    try:
        profile = user_to_edit.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user_to_edit)
    
    if request.method == 'POST':
        user_form = AdminUserEditForm(request.POST, request.FILES, instance=user_to_edit)
        profile_form = ExtendedProfileForm(request.POST, instance=profile)
        
        # Add paramedic form if user is paramedic
        paramedic_form = None
        if user_to_edit.is_paramedic():
            paramedic_form = AdminParamedicEditForm(request.POST, instance=user_to_edit)
        
        forms_valid = user_form.is_valid() and profile_form.is_valid()
        if paramedic_form:
            forms_valid = forms_valid and paramedic_form.is_valid()
        
        if forms_valid:
            user_form.save()
            profile_form.save()
            if paramedic_form:
                paramedic_form.save()
            messages.success(request, f'User {user_to_edit.username} has been updated successfully!')
            return redirect('accounts:manage_users')
    else:
        user_form = AdminUserEditForm(instance=user_to_edit)
        profile_form = ExtendedProfileForm(instance=profile)
        paramedic_form = AdminParamedicEditForm(instance=user_to_edit) if user_to_edit.is_paramedic() else None
    
    context = {
        'user_to_edit': user_to_edit,
        'user_form': user_form,
        'profile_form': profile_form,
        'paramedic_form': paramedic_form,
    }
    
    return render(request, 'accounts/admin_edit_user.html', context)


@login_required
def admin_delete_user_view(request, user_id):
    """Admin: Delete user"""
    if not request.user.is_admin_user():
        messages.error(request, 'Only admins can delete users.')
        return redirect('accounts:dashboard_redirect')
    
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user_to_delete == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User {username} has been deleted successfully!')
        return redirect('accounts:manage_users')
    
    context = {
        'user_to_delete': user_to_delete,
    }
    
    return render(request, 'accounts/admin_delete_user.html', context)


def password_reset_request_view(request):
    """Custom password reset request view"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset URL
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Prepare email context
                context = {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': 'Emergency Ambulance System',
                }
                
                # Render email templates
                subject = 'Password Reset - Emergency Ambulance System'
                html_message = render_to_string('accounts/emails/password_reset_email.html', context)
                plain_message = render_to_string('accounts/emails/password_reset_email.txt', context)
                
                # Send email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset email has been sent to your email address.')
                return redirect('accounts:password_reset_done')
                
            except User.DoesNotExist:
                # Don't reveal that the email doesn't exist
                messages.success(request, 'Password reset email has been sent to your email address.')
                return redirect('accounts:password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_done_view(request):
    """Password reset done view"""
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    """Password reset confirm view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('accounts:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        
        context = {
            'form': form,
            'validlink': True,
        }
    else:
        context = {
            'validlink': False,
        }
    
    return render(request, 'accounts/password_reset_confirm.html', context)


def password_reset_complete_view(request):
    """Password reset complete view"""
    return render(request, 'accounts/password_reset_complete.html')
