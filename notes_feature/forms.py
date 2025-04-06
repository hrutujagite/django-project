from django import forms
from .models import Notes

class NotesUploadForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [
        ('COMMON', 'Common (First Year)'),
        ('CS', 'Computer Science'),
        ('ME', 'Mechanical Engineering'),
        ('EE', 'Electrical Engineering'),
        # Add other departments...
    ]

    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, required=True)
    subject = forms.CharField(max_length=255, required=True, help_text="Enter subject name")
    tags = forms.CharField(
        max_length=255, required=False, 
        help_text="Enter comma-separated keywords (e.g., calculus, integration, limits)"
    )

    class Meta:
        model = Notes
        fields = ['title', 'department', 'semester', 'subject', 'tags', 'description', 'file']
