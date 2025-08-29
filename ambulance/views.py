from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.decorators import patient_required, paramedic_required, admin_required, staff_required
from .models import AmbulanceRequest, RequestStatusUpdate, Ambulance
from .forms import AmbulanceRequestForm, RequestStatusUpdateForm, AssignParamedicForm, AmbulanceForm, RequestFilterForm

User = get_user_model()


@login_required
@patient_required
def create_request(request):
    """Create new ambulance request (Patient only)"""
    if request.method == 'POST':
        form = AmbulanceRequestForm(request.POST)
        if form.is_valid():
            ambulance_request = form.save(commit=False)
            ambulance_request.patient = request.user
            ambulance_request.save()
            
            messages.success(request, 'Your ambulance request has been submitted successfully!')
            return redirect('ambulance:request_detail', pk=ambulance_request.pk)
    else:
        form = AmbulanceRequestForm()
    
    return render(request, 'ambulance/create_request.html', {'form': form})


@login_required
def request_detail(request, pk):
    """View ambulance request details"""
    ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk)
    
    # Check permissions
    if request.user.is_patient() and ambulance_request.patient != request.user:
        messages.error(request, 'You can only view your own requests.')
        return redirect('patient_dashboard')
    elif request.user.is_paramedic() and ambulance_request.paramedic != request.user and not request.user.is_admin_user():
        messages.error(request, 'You can only view requests assigned to you.')
        return redirect('paramedic_dashboard')
    
    # Get status updates
    status_updates = ambulance_request.status_updates.all().order_by('-timestamp')
    
    context = {
        'request': ambulance_request,
        'status_updates': status_updates,
    }
    
    return render(request, 'ambulance/request_detail.html', context)


@login_required
def request_list(request):
    """List ambulance requests with filtering"""
    requests = AmbulanceRequest.objects.all()
    
    # Filter based on user role
    if request.user.is_patient():
        requests = requests.filter(patient=request.user)
    elif request.user.is_paramedic():
        requests = requests.filter(
            Q(paramedic=request.user) | Q(status='pending')
        )
    
    # Apply filters
    filter_form = RequestFilterForm(request.GET, user=request.user)
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            requests = requests.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['priority']:
            requests = requests.filter(priority=filter_form.cleaned_data['priority'])
        if filter_form.cleaned_data['date_from']:
            requests = requests.filter(created_at__date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data['date_to']:
            requests = requests.filter(created_at__date__lte=filter_form.cleaned_data['date_to'])
        
        # Admin-specific filters
        if hasattr(filter_form, 'fields') and 'paramedic' in filter_form.fields:
            if filter_form.cleaned_data.get('paramedic'):
                requests = requests.filter(paramedic=filter_form.cleaned_data['paramedic'])
    
    # Order by priority and creation time
    requests = requests.order_by('-priority', '-created_at')
    
    # Pagination
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }
    
    return render(request, 'ambulance/request_list.html', context)


@login_required
@staff_required
def assign_paramedic(request, pk):
    """Assign paramedic to request (Admin/Paramedic)"""
    ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk)
    
    if request.method == 'POST':
        form = AssignParamedicForm(request.POST)
        if form.is_valid():
            paramedic = form.cleaned_data['paramedic']
            notes = form.cleaned_data['notes']
            
            # Update request
            old_status = ambulance_request.status
            ambulance_request.assign_paramedic(paramedic)
            
            # Create status update record
            RequestStatusUpdate.objects.create(
                request=ambulance_request,
                updated_by=request.user,
                old_status=old_status,
                new_status='assigned',
                notes=notes
            )
            
            messages.success(request, f'Request assigned to {paramedic.get_full_name() or paramedic.username}')
            return redirect('ambulance:request_detail', pk=pk)
    else:
        form = AssignParamedicForm()
    
    context = {
        'form': form,
        'request': ambulance_request,
    }
    
    return render(request, 'ambulance/assign_paramedic.html', context)


@login_required
@staff_required
def update_status(request, pk):
    """Update request status"""
    ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk)
    
    if request.method == 'POST':
        form = RequestStatusUpdateForm(request.POST)
        if form.is_valid():
            old_status = ambulance_request.status
            new_status = form.cleaned_data['new_status']
            notes = form.cleaned_data['notes']
            
            # Update request status
            ambulance_request.status = new_status
            if new_status == 'arrived':
                ambulance_request.mark_arrived()
            elif new_status == 'completed':
                ambulance_request.mark_completed()
            elif new_status == 'cancelled':
                ambulance_request.cancel_request()
            else:
                ambulance_request.save()
            
            # Create status update record
            RequestStatusUpdate.objects.create(
                request=ambulance_request,
                updated_by=request.user,
                old_status=old_status,
                new_status=new_status,
                notes=notes
            )
            
            messages.success(request, f'Request status updated to {ambulance_request.get_status_display()}')
            return redirect('ambulance:request_detail', pk=pk)
    else:
        form = RequestStatusUpdateForm()
    
    context = {
        'form': form,
        'request': ambulance_request,
    }
    
    return render(request, 'ambulance/update_status.html', context)


@login_required
@paramedic_required
def accept_request(request, pk):
    """Accept ambulance request (Paramedic only)"""
    ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk, status='pending')
    
    if request.method == 'POST':
        # Assign current paramedic to request
        old_status = ambulance_request.status
        ambulance_request.assign_paramedic(request.user)
        
        # Create status update record
        RequestStatusUpdate.objects.create(
            request=ambulance_request,
            updated_by=request.user,
            old_status=old_status,
            new_status='assigned',
            notes='Request accepted by paramedic'
        )
        
        messages.success(request, 'You have accepted this ambulance request.')
        return redirect('ambulance:request_detail', pk=pk)
    
    return render(request, 'ambulance/accept_request.html', {'request': ambulance_request})


@login_required
@admin_required
def ambulance_list(request):
    """List all ambulances (Admin only)"""
    ambulances = Ambulance.objects.all().order_by('vehicle_number')
    
    # Pagination
    paginator = Paginator(ambulances, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'ambulance/ambulance_list.html', context)


@login_required
@admin_required
def ambulance_create(request):
    """Create new ambulance (Admin only)"""
    if request.method == 'POST':
        form = AmbulanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance created successfully!')
            return redirect('ambulance:ambulance_list')
    else:
        form = AmbulanceForm()
    
    return render(request, 'ambulance/ambulance_form.html', {'form': form, 'title': 'Create Ambulance'})


@login_required
@admin_required
def ambulance_edit(request, pk):
    """Edit ambulance (Admin only)"""
    ambulance = get_object_or_404(Ambulance, pk=pk)
    
    if request.method == 'POST':
        form = AmbulanceForm(request.POST, instance=ambulance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance updated successfully!')
            return redirect('ambulance:ambulance_list')
    else:
        form = AmbulanceForm(instance=ambulance)
    
    context = {
        'form': form,
        'title': 'Edit Ambulance',
        'ambulance': ambulance,
    }
    
    return render(request, 'ambulance/ambulance_form.html', context)


@login_required
@require_http_methods(["POST"])
def quick_status_update(request, pk):
    """Quick status update via AJAX"""
    ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk)
    
    # Check permissions
    if not (request.user.is_admin_user() or 
            (request.user.is_paramedic() and ambulance_request.paramedic == request.user)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    new_status = request.POST.get('status')
    if new_status not in dict(AmbulanceRequest.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    old_status = ambulance_request.status
    ambulance_request.status = new_status
    
    # Handle special status updates
    if new_status == 'arrived':
        ambulance_request.mark_arrived()
    elif new_status == 'completed':
        ambulance_request.mark_completed()
    elif new_status == 'cancelled':
        ambulance_request.cancel_request()
    else:
        ambulance_request.save()
    
    # Create status update record
    RequestStatusUpdate.objects.create(
        request=ambulance_request,
        updated_by=request.user,
        old_status=old_status,
        new_status=new_status,
        notes='Quick status update'
    )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'status_display': ambulance_request.get_status_display()
    })
