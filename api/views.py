from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from accounts.models import UserProfile
from ambulance.models import AmbulanceRequest, RequestStatusUpdate, Ambulance
from .serializers import (
    UserSerializer, UserProfileSerializer, ParamedicSerializer,
    AmbulanceRequestSerializer, AmbulanceRequestCreateSerializer,
    RequestStatusUpdateSerializer, AmbulanceSerializer,
    AssignParamedicSerializer, StatusUpdateSerializer, DashboardStatsSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for User model"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin_user():
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParamedicViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Paramedic users"""
    
    serializer_class = ParamedicSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='paramedic')
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available paramedics"""
        paramedics = User.objects.filter(role='paramedic', is_available=True)
        serializer = self.get_serializer(paramedics, many=True)
        return Response(serializer.data)


class AmbulanceRequestViewSet(viewsets.ModelViewSet):
    """API ViewSet for AmbulanceRequest model"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AmbulanceRequestCreateSerializer
        return AmbulanceRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = AmbulanceRequest.objects.all()
        
        if user.is_patient():
            queryset = queryset.filter(patient=user)
        elif user.is_paramedic():
            queryset = queryset.filter(
                Q(paramedic=user) | Q(status='pending')
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign_paramedic(self, request, pk=None):
        """Assign paramedic to request"""
        if not (request.user.is_admin_user() or request.user.is_paramedic()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        ambulance_request = self.get_object()
        serializer = AssignParamedicSerializer(data=request.data)
        
        if serializer.is_valid():
            paramedic_id = serializer.validated_data['paramedic_id']
            notes = serializer.validated_data.get('notes', '')
            
            paramedic = get_object_or_404(User, id=paramedic_id, role='paramedic')
            old_status = ambulance_request.status
            ambulance_request.assign_paramedic(paramedic)
            
            # Create status update record
            RequestStatusUpdate.objects.create(
                request=ambulance_request,
                updated_by=request.user,
                old_status=old_status,
                new_status='assigned',
                notes=notes
            )
            
            return Response({
                'message': f'Request assigned to {paramedic.get_full_name() or paramedic.username}',
                'request': AmbulanceRequestSerializer(ambulance_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update request status"""
        ambulance_request = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin_user() or 
                (request.user.is_paramedic() and ambulance_request.paramedic == request.user)):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StatusUpdateSerializer(
            data=request.data, 
            context={'request_obj': ambulance_request}
        )
        
        if serializer.is_valid():
            old_status = ambulance_request.status
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            
            # Update request status
            ambulance_request.status = new_status
            if new_status == 'arrived':
                ambulance_request.mark_arrived()
            elif new_status == 'completed':
                ambulance_request.mark_completed()
            elif new_status == 'cancelled':
                ambulance_request.cancel_request()
            else:
                ambulance_request.save()
            
            # Create status update record
            RequestStatusUpdate.objects.create(
                request=ambulance_request,
                updated_by=request.user,
                old_status=old_status,
                new_status=new_status,
                notes=notes
            )
            
            return Response({
                'message': f'Status updated to {ambulance_request.get_status_display()}',
                'request': AmbulanceRequestSerializer(ambulance_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept request (Paramedic only)"""
        if not request.user.is_paramedic():
            return Response(
                {'error': 'Only paramedics can accept requests'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        ambulance_request = get_object_or_404(AmbulanceRequest, pk=pk, status='pending')
        old_status = ambulance_request.status
        ambulance_request.assign_paramedic(request.user)
        
        # Create status update record
        RequestStatusUpdate.objects.create(
            request=ambulance_request,
            updated_by=request.user,
            old_status=old_status,
            new_status='assigned',
            notes='Request accepted by paramedic'
        )
        
        return Response({
            'message': 'Request accepted successfully',
            'request': AmbulanceRequestSerializer(ambulance_request).data
        })
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Get status update history for request"""
        ambulance_request = self.get_object()
        status_updates = ambulance_request.status_updates.all().order_by('-timestamp')
        serializer = RequestStatusUpdateSerializer(status_updates, many=True)
        return Response(serializer.data)


class AmbulanceViewSet(viewsets.ModelViewSet):
    """API ViewSet for Ambulance model"""
    
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin_user():
            return Ambulance.objects.all()
        elif self.request.user.is_paramedic():
            return Ambulance.objects.filter(
                Q(assigned_paramedic=self.request.user) | Q(status='available')
            )
        else:
            return Ambulance.objects.filter(status='available')
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available ambulances"""
        ambulances = Ambulance.objects.filter(status='available')
        serializer = self.get_serializer(ambulances, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    
    # Base statistics
    stats = {
        'total_requests': AmbulanceRequest.objects.count(),
        'pending_requests': AmbulanceRequest.objects.filter(status='pending').count(),
        'active_requests': AmbulanceRequest.objects.filter(
            status__in=['assigned', 'en_route', 'arrived']
        ).count(),
        'completed_requests': AmbulanceRequest.objects.filter(status='completed').count(),
        'available_paramedics': User.objects.filter(role='paramedic', is_available=True).count(),
    }
    
    # Role-specific statistics
    if user.is_patient():
        stats['my_requests'] = AmbulanceRequest.objects.filter(patient=user).count()
    elif user.is_paramedic():
        stats['assigned_to_me'] = AmbulanceRequest.objects.filter(
            paramedic=user, status__in=['assigned', 'en_route', 'arrived']
        ).count()
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_requests(request):
    """Get recent requests based on user role"""
    user = request.user
    
    if user.is_patient():
        requests = AmbulanceRequest.objects.filter(patient=user)
    elif user.is_paramedic():
        requests = AmbulanceRequest.objects.filter(
            Q(paramedic=user) | Q(status='pending')
        )
    else:  # Admin
        requests = AmbulanceRequest.objects.all()
    
    requests = requests.order_by('-created_at')[:10]
    serializer = AmbulanceRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_paramedic_availability(request):
    """Toggle paramedic availability"""
    if not request.user.is_paramedic():
        return Response(
            {'error': 'Only paramedics can toggle availability'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    request.user.is_available = not request.user.is_available
    request.user.save()
    
    return Response({
        'is_available': request.user.is_available,
        'status_text': 'Available' if request.user.is_available else 'Unavailable'
    })
