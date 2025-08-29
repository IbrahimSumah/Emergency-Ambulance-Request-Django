from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles.
    
    Args:
        allowed_roles: List of allowed roles or single role string
    
    Usage:
        @role_required(['admin', 'paramedic'])
        @role_required('patient')
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:dashboard_redirect')
        return _wrapped_view
    return decorator


def patient_required(view_func):
    """Decorator to restrict access to patients only"""
    return role_required('patient')(view_func)


def paramedic_required(view_func):
    """Decorator to restrict access to paramedics only"""
    return role_required('paramedic')(view_func)


def admin_required(view_func):
    """Decorator to restrict access to admins only"""
    return role_required('admin')(view_func)


def staff_required(view_func):
    """Decorator to restrict access to staff (paramedics and admins)"""
    return role_required(['paramedic', 'admin'])(view_func)

