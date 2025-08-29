from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('paramedic', 'Paramedic'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True, help_text="Any medical conditions or allergies")
    
    # Paramedic specific fields
    license_number = models.CharField(max_length=50, blank=True, null=True, help_text="For paramedics only")
    is_available = models.BooleanField(default=True, help_text="For paramedics - availability status")
    
    # Profile image
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_patient(self):
        return self.role == 'patient'
    
    def is_paramedic(self):
        return self.role == 'paramedic'
    
    def is_admin_user(self):
        return self.role == 'admin'
    
    class Meta:
        db_table = 'accounts_user'


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        db_table = 'accounts_userprofile'
