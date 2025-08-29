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
    
    # Admin Management
    path('manage-users/', views.manage_users_view, name='manage_users'),
    
    # AJAX endpoints
    path('api/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    
    # Dashboard redirect
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]

