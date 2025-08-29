from django.urls import path
from . import views

app_name = 'ambulance'

urlpatterns = [
    # Request URLs
    path('request/create/', views.create_request, name='create_request'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/assigned/', views.paramedic_assigned_list, name='paramedic_assigned'),
    path('requests/pending/', views.paramedic_pending_list, name='paramedic_pending'),
    
    # Request management URLs
    path('request/<int:pk>/assign/', views.assign_paramedic, name='assign_paramedic'),
    path('request/<int:pk>/update-status/', views.update_status, name='update_status'),
    path('request/<int:pk>/accept/', views.accept_request, name='accept_request'),
    
    # Ambulance management URLs (Admin only)
    path('ambulances/', views.ambulance_list, name='ambulance_list'),
    path('ambulance/create/', views.ambulance_create, name='ambulance_create'),
    path('ambulance/<int:pk>/edit/', views.ambulance_edit, name='ambulance_edit'),
    path('ambulance/<int:pk>/delete/', views.ambulance_delete, name='ambulance_delete'),
    
    # AJAX endpoints
    path('api/request/<int:pk>/quick-status/', views.quick_status_update, name='quick_status_update'),
]

