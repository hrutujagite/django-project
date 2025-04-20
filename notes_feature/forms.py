from django import forms
from .models import Notes

class NotesUploadForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [
        ('', 'Select Department'),
        ('HUMANITIES', 'Humanities'),
        ('COMPUTER', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('EXTC', 'Electronics & Telecommunication'),
        ('ELECTRICAL', 'Electrical Engineering'),
        ('MECHANICAL', 'Mechanical Engineering'),
    ]

    SEMESTER_CHOICES = [
        ('', 'Select Semester'),
    ] + [(i, f"Semester {i}") for i in range(1, 9)]

    title = forms.CharField(
        max_length=255, 
        required=True,
        help_text="Enter the title of your notes *"
    )
    
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES, 
        required=True,
        help_text="Select your department *"
    )
    
    semester = forms.ChoiceField(
        choices=SEMESTER_CHOICES, 
        required=True,
        help_text="Select your semester *"
    )
    
    subject = forms.CharField(
        max_length=255, 
        required=True,
        help_text="Enter subject name *"
    )
    
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Enter a description of your notes (optional)"
    )
    
    tags = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Example: python, programming, loops, functions, arrays",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by commas...'
        })
    )

    file = forms.FileField(
        required=True,
        help_text="Upload your notes file *"
    )

    class Meta:
        model = Notes
        fields = ['title', 'department', 'semester', 'subject', 'description', 'tags', 'file']
