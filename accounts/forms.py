from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User

# registration form 
class UserRegistrationForm(UserCreationForm):
    USER_TYPES = User.USER_TYPE_CHOICES
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs= { 
        'class':'form-control',
        'placeholder':'Email'}))
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, widget=forms.Select(attrs={
        'class' : 'form-control'
    }))
   
    
    kra_pin = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional for Admin/Manager'})
    )
    national_id = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID'})
    )

    class Meta:
        model = User 
        fields = ('username', 'email', 'user_type', 'password1', 'password2', 'kra_pin', 'national_id') # simply the form fields my user will fill
        widgets = {
            'username' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder' : 'Username'
            })
        }
        
    # passwords
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class' : 'form-control', 'placeholder' : 'password'})
        self.fields['password2'].widget.attrs.update({'class':'form-control', 'placeholder': 'Confirm Password'})
        
        self.fields['kra_pin'].widget.attrs['class'] = 'form-control'
        self.fields['national_id'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type in ['admin', 'manager']:
            if not cleaned_data.get('national_id'):
                raise forms.ValidationError("National ID is required for Admin/Manager.")
            if not cleaned_data.get('kra_pin'):
                raise forms.ValidationError("KRA PIN is required for Admin/Manager.")
        return cleaned_data
    
# login form 
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder' : 'Username'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'password'
    }))

# profile form : update on account profile 
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','bio','profile_image')
        widgets = {
            'username' : forms.TextInput(attrs={'class' : 'form-control'}),
            'email' :forms.TextInput(attrs={'class' : 'form-control'}),
            'bio' :forms.Textarea(attrs={'class' : 'form-control', 'rows' : 3})
        }

