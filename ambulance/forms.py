from django import forms
from django.contrib.auth import get_user_model
from .models import AmbulanceRequest, RequestStatusUpdate, Ambulance

User = get_user_model()


class AmbulanceRequestForm(forms.ModelForm):
    """Form for creating ambulance requests"""
    
    class Meta:
        model = AmbulanceRequest
        fields = [
            'pickup_address', 'destination_address', 'description', 
            'priority', 'contact_phone', 'pickup_latitude', 'pickup_longitude',
            'destination_latitude', 'destination_longitude'
        ]
        widgets = {
            'pickup_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the pickup address'}),
            'destination_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter destination (hospital/clinic)'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the emergency situation'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Contact phone number'}),
            'pickup_latitude': forms.HiddenInput(),
            'pickup_longitude': forms.HiddenInput(),
            'destination_latitude': forms.HiddenInput(),
            'destination_longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name not in ['pickup_latitude', 'pickup_longitude', 'destination_latitude', 'destination_longitude']:
                if field_name == 'priority':
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
        
        # Make some fields required
        self.fields['pickup_address'].required = True
        self.fields['description'].required = True
        self.fields['contact_phone'].required = True


class RequestStatusUpdateForm(forms.ModelForm):
    """Form for updating request status"""
    
    class Meta:
        model = RequestStatusUpdate
        fields = ['new_status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add notes about this status update'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        self.fields['new_status'].widget.attrs['class'] = 'form-select'
        self.fields['notes'].widget.attrs['class'] = 'form-control'


class AssignParamedicForm(forms.Form):
    """Form for assigning paramedic to request"""
    
    paramedic = forms.ModelChoiceField(
        queryset=User.objects.filter(role='paramedic', is_available=True),
        empty_label="Select a paramedic",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Assignment notes (optional)'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refresh queryset to get current available paramedics
        self.fields['paramedic'].queryset = User.objects.filter(
            role='paramedic', 
            is_available=True
        ).order_by('first_name', 'last_name')


class AmbulanceForm(forms.ModelForm):
    """Form for managing ambulance vehicles"""
    
    class Meta:
        model = Ambulance
        fields = [
            'vehicle_number', 'license_plate', 'model', 'year', 
            'status', 'assigned_paramedic', 'current_latitude', 'current_longitude'
        ]
        widgets = {
            'current_latitude': forms.HiddenInput(),
            'current_longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name not in ['current_latitude', 'current_longitude']:
                if field_name in ['status', 'assigned_paramedic']:
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
        
        # Filter paramedics for assignment
        self.fields['assigned_paramedic'].queryset = User.objects.filter(role='paramedic')
        self.fields['assigned_paramedic'].empty_label = "No paramedic assigned"


class RequestFilterForm(forms.Form):
    """Form for filtering ambulance requests"""
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(AmbulanceRequest.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(AmbulanceRequest.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add paramedic filter for admin users
        if user and user.is_admin_user():
            paramedics = User.objects.filter(role='paramedic').order_by('first_name', 'last_name')
            self.fields['paramedic'] = forms.ModelChoiceField(
                queryset=paramedics,
                required=False,
                empty_label="All Paramedics",
                widget=forms.Select(attrs={'class': 'form-select'})
            )

