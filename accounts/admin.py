from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_available', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_available', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'emergency_contact', 'medical_conditions', 'profile_image')
        }),
        ('Paramedic Info', {
            'fields': ('license_number', 'is_available'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'phone_number', 'address', 'email')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model"""
    
    list_display = ('user', 'location', 'email_notifications', 'sms_notifications', 'created_at')
    list_filter = ('email_notifications', 'sms_notifications', 'created_at')
    search_fields = ('user__username', 'user__email', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'location', 'website')
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
