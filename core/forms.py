import re
from django import forms
from .models import Profile 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm


# Custom email validator function
def validate_email(value):
    # Check for student email (roll number + branch)
    if re.match(r'^[0-9]{7}@comp\.fcrit\.ac\.in$', value):
        return value  # valid student email
    # Check for teacher email (anything@fcrit.ac.in)
    elif re.match(r'^[a-zA-Z]+(\.[a-zA-Z]+)*@fcrit\.ac\.in$', value):
        return value  # valid teacher email
    else:
        raise ValidationError("Please enter a valid FCRIT email address.")



# SignUpForm for user registration
class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)  # ✅ Added first name
    last_name = forms.CharField(max_length=30, required=True)   # ✅ Added last name
    username = forms.CharField(max_length=100)
    email = forms.EmailField(validators=[validate_email])  # ✅ Enforcing FCRIT email format
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return first_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return last_name
    # Validate username availability
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different one.")
        return username
    
    # Validate email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different one.")
        return email

    # Validate that the password and confirmation password match
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        # Ensure the passwords match
        if password != password_confirm:
            raise ValidationError("Passwords do not match.")
        
        return password  # Return password, since that's what's needed to create the user
    
    # Optional: You can add additional validations if required
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data  # ✅ Fixed return statement




# Form for User model fields (username, first_name, last_name)
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user instance passed in kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
# Form for password change

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
