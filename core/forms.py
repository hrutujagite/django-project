from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

# Custom email validator function
def validate_email(value):
    # Check for student email (roll number + branch)
    if re.match(r'^[a-zA-Z0-9]+@[a-zA-Z]+\.fcrit\.ac\.in$', value):
        return value  # valid student email
    # Check for teacher email (anything@fcrit.ac.in)
    elif re.match(r'^[a-zA-Z0-9]+@fcrit\.ac\.in$', value):
        return value  # valid teacher email
    else:
        raise ValidationError("Please enter a valid FCRIT email address.")

# SignUpForm for user registration
class SignUpForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField(validators=[validate_email])  # Applying the custom email validator
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    # Validate username availability
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different one.")
        return username
    
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
        
        # You can apply any additional form-wide validation here, if necessary
        
        return cleaned_data
