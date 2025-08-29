from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from accounts.decorators import patient_required, paramedic_required, admin_required
from ambulance.models import AmbulanceRequest, Ambulance

User = get_user_model()


@login_required
@patient_required
def patient_dashboard(request):
    """Patient dashboard view"""
    user = request.user
    
    # Get patient's requests
    my_requests = AmbulanceRequest.objects.filter(patient=user).order_by('-created_at')
    
    # Statistics
    stats = {
        'total_requests': my_requests.count(),
        'pending_requests': my_requests.filter(status='pending').count(),
        'active_requests': my_requests.filter(status__in=['assigned', 'en_route', 'arrived']).count(),
        'completed_requests': my_requests.filter(status='completed').count(),
    }
    
    # Recent requests
    recent_requests = my_requests[:5]
    
    context = {
        'stats': stats,
        'recent_requests': recent_requests,
        'user': user,
    }
    
    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
@paramedic_required
def paramedic_dashboard(request):
    """Paramedic dashboard view"""
    user = request.user
    
    # Get paramedic's assigned requests
    assigned_requests = AmbulanceRequest.objects.filter(paramedic=user).order_by('-created_at')
    
    # Get pending requests (available to accept)
    pending_requests = AmbulanceRequest.objects.filter(status='pending').order_by('-created_at')
    
    # Statistics
    stats = {
        'assigned_to_me': assigned_requests.filter(status__in=['assigned', 'en_route', 'arrived']).count(),
        'completed_by_me': assigned_requests.filter(status='completed').count(),
        'pending_requests': pending_requests.count(),
        'total_handled': assigned_requests.count(),
    }
    
    # Recent assigned requests
    recent_assigned = assigned_requests[:5]
    
    # Recent pending requests
    recent_pending = pending_requests[:5]
    
    context = {
        'stats': stats,
        'recent_assigned': recent_assigned,
        'recent_pending': recent_pending,
        'user': user,
    }
    
    return render(request, 'dashboard/paramedic_dashboard.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    user = request.user
    
    # Get all requests
    all_requests = AmbulanceRequest.objects.all().order_by('-created_at')
    
    # Statistics
    stats = {
        'total_requests': all_requests.count(),
        'pending_requests': all_requests.filter(status='pending').count(),
        'active_requests': all_requests.filter(status__in=['assigned', 'en_route', 'arrived']).count(),
        'completed_requests': all_requests.filter(status='completed').count(),
        'cancelled_requests': all_requests.filter(status='cancelled').count(),
        'total_users': User.objects.count(),
        'patients': User.objects.filter(role='patient').count(),
        'paramedics': User.objects.filter(role='paramedic').count(),
        'available_paramedics': User.objects.filter(role='paramedic', is_available=True).count(),
        'total_ambulances': Ambulance.objects.count(),
        'available_ambulances': Ambulance.objects.filter(status='available').count(),
    }
    
    # Recent requests
    recent_requests = all_requests[:10]
    
    # Priority distribution
    priority_stats = all_requests.values('priority').annotate(count=Count('priority')).order_by('priority')
    
    # Status distribution
    status_stats = all_requests.values('status').annotate(count=Count('status')).order_by('status')
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'stats': stats,
        'recent_requests': recent_requests,
        'priority_stats': priority_stats,
        'status_stats': status_stats,
        'recent_users': recent_users,
        'user': user,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@admin_required
def admin_reports(request):
    """Admin analytics/Reports page"""
    user = request.user
    
    # Basic aggregates (expand as needed)
    requests_qs = AmbulanceRequest.objects.all()
    kpis = {
        'total': requests_qs.count(),
        'pending': requests_qs.filter(status='pending').count(),
        'assigned': requests_qs.filter(status='assigned').count(),
        'en_route': requests_qs.filter(status='en_route').count(),
        'arrived': requests_qs.filter(status='arrived').count(),
        'completed': requests_qs.filter(status='completed').count(),
        'cancelled': requests_qs.filter(status='cancelled').count(),
    }
    
    by_priority = list(requests_qs.values('priority').annotate(count=Count('priority')).order_by('priority'))
    by_status = list(requests_qs.values('status').annotate(count=Count('status')).order_by('status'))
    
    context = {
        'kpis': kpis,
        'by_priority': by_priority,
        'by_status': by_status,
        'user': user,
    }
    return render(request, 'dashboard/admin_reports.html', context)
