from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from ambulance.models import AmbulanceRequest, RequestStatusUpdate, Ambulance

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'phone_number', 'is_available', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'bio', 'location', 'website', 
            'email_notifications', 'sms_notifications'
        ]


class ParamedicSerializer(serializers.ModelSerializer):
    """Serializer for Paramedic users"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'phone_number', 'is_available', 'license_number'
        ]
        read_only_fields = ['id', 'username']


class AmbulanceRequestSerializer(serializers.ModelSerializer):
    """Serializer for AmbulanceRequest model"""
    
    patient = UserSerializer(read_only=True)
    paramedic = ParamedicSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = AmbulanceRequest
        fields = [
            'id', 'patient', 'paramedic', 'pickup_address', 'destination_address',
            'pickup_latitude', 'pickup_longitude', 'destination_latitude', 'destination_longitude',
            'description', 'priority', 'priority_display', 'status', 'status_display',
            'contact_phone', 'created_at', 'updated_at', 'assigned_at', 'completed_at',
            'estimated_arrival_time', 'actual_arrival_time', 'notes', 'is_active'
        ]
        read_only_fields = [
            'id', 'patient', 'paramedic', 'created_at', 'updated_at', 
            'assigned_at', 'completed_at', 'actual_arrival_time', 'is_active'
        ]


class AmbulanceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AmbulanceRequest"""
    
    class Meta:
        model = AmbulanceRequest
        fields = [
            'pickup_address', 'destination_address', 'pickup_latitude', 'pickup_longitude',
            'destination_latitude', 'destination_longitude', 'description', 
            'priority', 'contact_phone'
        ]
    
    def create(self, validated_data):
        # Set patient from request context
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class RequestStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for RequestStatusUpdate model"""
    
    updated_by = UserSerializer(read_only=True)
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    
    class Meta:
        model = RequestStatusUpdate
        fields = [
            'id', 'updated_by', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'notes', 'timestamp'
        ]
        read_only_fields = ['id', 'updated_by', 'timestamp']


class AmbulanceSerializer(serializers.ModelSerializer):
    """Serializer for Ambulance model"""
    
    assigned_paramedic = ParamedicSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Ambulance
        fields = [
            'id', 'vehicle_number', 'license_plate', 'current_latitude', 'current_longitude',
            'status', 'status_display', 'assigned_paramedic', 'model', 'year',
            'created_at', 'updated_at', 'is_available'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available']


class AssignParamedicSerializer(serializers.Serializer):
    """Serializer for assigning paramedic to request"""
    
    paramedic_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_paramedic_id(self, value):
        try:
            paramedic = User.objects.get(id=value, role='paramedic')
            if not paramedic.is_available:
                raise serializers.ValidationError("Selected paramedic is not available.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid paramedic ID.")


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating request status"""
    
    status = serializers.ChoiceField(choices=AmbulanceRequest.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        request_obj = self.context.get('request_obj')
        if request_obj and request_obj.status == value:
            raise serializers.ValidationError("Request is already in this status.")
        return value


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    active_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    available_paramedics = serializers.IntegerField()
    
    # Optional fields for different user roles
    my_requests = serializers.IntegerField(required=False)
    assigned_to_me = serializers.IntegerField(required=False)

