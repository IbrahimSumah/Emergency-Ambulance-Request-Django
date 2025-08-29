from django.urls import path
from . import dashboard_views

urlpatterns = [
    path('patient/', dashboard_views.patient_dashboard, name='patient_dashboard'),
    path('paramedic/', dashboard_views.paramedic_dashboard, name='paramedic_dashboard'),
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('reports/', dashboard_views.admin_reports, name='admin_reports'),
]

