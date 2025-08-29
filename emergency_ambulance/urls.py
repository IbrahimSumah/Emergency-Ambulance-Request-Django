"""
URL configuration for emergency_ambulance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    """Redirect home to login page"""
    return redirect('accounts:login')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home redirect
    path('', home_redirect, name='home'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('ambulance/', include('ambulance.urls')),
    path('api/v1/', include('api.urls')),
    
    # Dashboard URLs (will be created in Phase 7)
    path('dashboard/', include('emergency_ambulance.dashboard_urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
