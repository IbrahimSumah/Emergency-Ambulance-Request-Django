from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),
    
    # Admin Management
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('admin/edit-user/<int:user_id>/', views.admin_edit_user_view, name='admin_edit_user'),
    path('admin/delete-user/<int:user_id>/', views.admin_delete_user_view, name='admin_delete_user'),
    
    # AJAX endpoints
    path('api/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    
    # Dashboard redirect
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]

