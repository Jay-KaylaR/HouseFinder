from django import forms
from django.forms import ModelMultipleChoiceField
from .models import Property, PropertyImage, Category

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'price', 'status', 'category', 
            'location', 'lat', 'lng', 'bedrooms', 'bathrooms', 'cover_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Spacious 3BR Nyali Apartment'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the property features, amenities, and what makes it special...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 25000',
                'min': '0',
                'step': '100'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Nyali, Mombasa'
            }),
            'lat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. -4.0435',
                'step': 'any'
            }),
            'lng': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 39.6682',
                'step': 'any'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10'
            }),
            'cover_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize labels
        self.fields['price'].label = 'Price (KSh)'
        self.fields['status'].label = 'Availability'
        self.fields['bedrooms'].label = 'Bedrooms'
        self.fields['bathrooms'].label = 'Bathrooms'
        self.fields['cover_image'].label = 'Cover Image (Optional)'

        # Add help text
        self.fields['lat'].help_text = 'Get coordinates from Google Maps (right-click on location)'
        self.fields['lng'].help_text = 'Get coordinates from Google Maps (right-click on location)'
        self.fields['cover_image'].help_text = 'Upload main property image (JPG/PNG, max 5MB)'

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        
        if lat is not None and lng is not None:
            if not (-90 <= lat <= 90):
                raise forms.ValidationError('Latitude must be between -90 and 90.')
            if not (-180 <= lng <= 180):
                raise forms.ValidationError('Longitude must be between -180 and 180.')
        
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    """For adding images after property creation"""
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Living room view'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class InquiryForm(forms.Form):
    """Simple inquiry form from property detail page"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'I am interested in this property. When can I view it?'
        }),
        max_length=500,
        required=True
    )

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Message should be at least 10 characters long.')
        return message
