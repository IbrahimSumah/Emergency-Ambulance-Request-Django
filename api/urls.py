from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'paramedics', views.ParamedicViewSet, basename='paramedic')
router.register(r'requests', views.AmbulanceRequestViewSet, basename='ambulancerequest')
router.register(r'ambulances', views.AmbulanceViewSet, basename='ambulance')

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Additional API endpoints
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/recent-requests/', views.recent_requests, name='recent_requests'),
    path('paramedic/toggle-availability/', views.toggle_paramedic_availability, name='toggle_availability'),
    
    # DRF Auth
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

