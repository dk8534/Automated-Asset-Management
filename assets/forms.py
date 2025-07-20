from django import forms
from django.contrib.auth.models import User
from .models import Asset, AssetAssignment, UserProfile

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['serial_number', 'display_name', 'department', 'model_category', 'status', 'company']
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'model_category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        is_new_asset = kwargs.pop('is_new_asset', False)
        
        print(f"DEBUG: AssetForm init - user_role: {user_role}, is_new_asset: {is_new_asset}")

        super().__init__(*args, **kwargs)

        # --- FIX FOR SERIAL NUMBER VISIBILITY AND EDITABILITY ---
        # Serial number should ONLY be editable when creating a NEW asset (and only by admin).
        # For existing assets (editing), it should always be disabled but visible.
        if not is_new_asset:
            self.fields['serial_number'].widget.attrs['disabled'] = True
            self.fields['serial_number'].required = False # Not required if disabled
            # REMOVE THE LINE BELOW:
            # if 'serial_number' in self.fields:
            #     del self.fields['serial_number']
        # --- END FIX ---

        # Apply role-based field permissions
        if user_role == 'admin':
            # Admin: Status field is ALWAYS disabled.
            if is_new_asset:
                self.initial['status'] = 'available'
            self.fields['status'].widget.attrs['disabled'] = True
            self.fields['status'].required = False # Not required if disabled

            # All other fields (display_name, department, category, company) are editable for admin.
            # serial_number is handled by the 'if not is_new_asset' block above.

        elif user_role == 'asset_incharge':
            # Asset Incharge: Can only edit status and department.
            # First, disable ALL fields that are not status or department.
            # serial_number is already handled by 'if not is_new_asset' block.
            for field_name in self.fields:
                if field_name not in ['status', 'department']:
                    self.fields[field_name].widget.attrs['disabled'] = True
                    self.fields[field_name].required = False # Not required if disabled

            # Explicitly ENABLE status and department.
            self.fields['status'].widget.attrs.pop('disabled', None)
            self.fields['status'].required = True

            self.fields['department'].widget.attrs.pop('disabled', None)
            self.fields['department'].required = True

        # For 'user' role, all fields will remain disabled by default (as they don't have edit access to this form)
        # The @user_passes_test decorator in views.py already restricts access to this form for 'user' role.


class AssetAssignmentForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__role='user'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select User"
    )
    
    class Meta:
        model = AssetAssignment
        fields = ['assigned_to', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
