from django import forms
from .models import Answer, AnswerImage

class AnswerForm(forms.ModelForm):
    """Form for submitting answers."""
    content = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Write your answer here...", "rows": 4}),
        label="Your Answer"
    )

    class Meta:
        model = Answer
        fields = ['content']
