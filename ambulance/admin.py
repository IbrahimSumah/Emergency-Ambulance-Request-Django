from django.contrib import admin
from .models import AmbulanceRequest, RequestStatusUpdate, Ambulance


@admin.register(AmbulanceRequest)
class AmbulanceRequestAdmin(admin.ModelAdmin):
    """Admin configuration for AmbulanceRequest model"""
    
    list_display = ('id', 'patient', 'paramedic', 'status', 'priority', 'created_at', 'assigned_at')
    list_filter = ('status', 'priority', 'created_at', 'assigned_at')
    search_fields = ('patient__username', 'paramedic__username', 'pickup_address', 'description')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at', 'completed_at', 'actual_arrival_time')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('patient', 'paramedic', 'status', 'priority', 'description')
        }),
        ('Location Details', {
            'fields': ('pickup_address', 'pickup_latitude', 'pickup_longitude', 
                      'destination_address', 'destination_latitude', 'destination_longitude')
        }),
        ('Contact & Time Information', {
            'fields': ('contact_phone', 'estimated_arrival_time', 'actual_arrival_time')
        }),
        ('Notes & Status', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'assigned_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected requests as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} requests marked as completed.')
    mark_as_completed.short_description = "Mark selected requests as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected requests as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} requests marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected requests as cancelled"


@admin.register(RequestStatusUpdate)
class RequestStatusUpdateAdmin(admin.ModelAdmin):
    """Admin configuration for RequestStatusUpdate model"""
    
    list_display = ('request', 'old_status', 'new_status', 'updated_by', 'timestamp')
    list_filter = ('old_status', 'new_status', 'timestamp')
    search_fields = ('request__id', 'updated_by__username', 'notes')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Status Change', {
            'fields': ('request', 'old_status', 'new_status', 'updated_by')
        }),
        ('Additional Information', {
            'fields': ('notes', 'timestamp')
        }),
    )


@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    """Admin configuration for Ambulance model"""
    
    list_display = ('vehicle_number', 'license_plate', 'status', 'assigned_paramedic', 'model', 'year')
    list_filter = ('status', 'year', 'created_at')
    search_fields = ('vehicle_number', 'license_plate', 'model', 'assigned_paramedic__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('vehicle_number',)
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('vehicle_number', 'license_plate', 'model', 'year', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_paramedic',)
        }),
        ('Location', {
            'fields': ('current_latitude', 'current_longitude'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_maintenance']
    
    def mark_as_available(self, request, queryset):
        """Mark selected ambulances as available"""
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} ambulances marked as available.')
    mark_as_available.short_description = "Mark selected ambulances as available"
    
    def mark_as_maintenance(self, request, queryset):
        """Mark selected ambulances as under maintenance"""
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'{updated} ambulances marked as under maintenance.')
    mark_as_maintenance.short_description = "Mark selected ambulances as under maintenance"
