from django.db import models
from django.conf import settings
from django.utils import timezone


class AmbulanceRequest(models.Model):
    """Model for ambulance requests"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('en_route', 'En Route'),
        ('arrived', 'Arrived'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    # Request details
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ambulance_requests')
    paramedic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    
    # Location information
    pickup_address = models.TextField(help_text="Address where ambulance should pick up patient")
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    destination_address = models.TextField(blank=True, null=True, help_text="Hospital or destination address")
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Request information
    description = models.TextField(help_text="Description of the emergency")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact information
    contact_phone = models.CharField(max_length=15, help_text="Contact phone number for this request")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Estimated times
    estimated_arrival_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True, null=True, help_text="Additional notes from paramedic or admin")
    
    # Assigned ambulance (optional)
    ambulance = models.ForeignKey('Ambulance', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    
    def __str__(self):
        return f"Request #{self.id} - {self.patient.username} ({self.get_status_display()})"
    
    def assign_paramedic(self, paramedic):
        """Assign a paramedic to this request"""
        self.paramedic = paramedic
        self.status = 'assigned'
        self.assigned_at = timezone.now()
        self.save()
    
    def mark_en_route(self):
        """Mark request as en route"""
        self.status = 'en_route'
        self.save()
    
    def mark_arrived(self):
        """Mark request as arrived"""
        self.status = 'arrived'
        self.actual_arrival_time = timezone.now()
        self.save()
    
    def mark_completed(self):
        """Mark request as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel_request(self):
        """Cancel the request"""
        self.status = 'cancelled'
        self.save()
    
    @property
    def is_active(self):
        """Check if request is still active"""
        return self.status not in ['completed', 'cancelled']
    
    class Meta:
        db_table = 'ambulance_request'
        ordering = ['-created_at']


class RequestStatusUpdate(models.Model):
    """Model to track status updates for ambulance requests"""
    
    request = models.ForeignKey(AmbulanceRequest, on_delete=models.CASCADE, related_name='status_updates')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    old_status = models.CharField(max_length=20, choices=AmbulanceRequest.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=AmbulanceRequest.STATUS_CHOICES)
    
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Request #{self.request.id}: {self.old_status} → {self.new_status}"
    
    class Meta:
        db_table = 'ambulance_request_status_update'
        ordering = ['-timestamp']


class Ambulance(models.Model):
    """Model for ambulance vehicles"""
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
        ('out_of_service', 'Out of Service'),
    )
    
    vehicle_number = models.CharField(max_length=20, unique=True)
    license_plate = models.CharField(max_length=15, unique=True)
    
    # Current location
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Assigned paramedic
    assigned_paramedic = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_ambulance'
    )
    
    # Vehicle details
    model = models.CharField(max_length=50, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Ambulance {self.vehicle_number} ({self.get_status_display()})"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    class Meta:
        db_table = 'ambulance_vehicle'
        ordering = ['vehicle_number']
