from django.contrib import admin
from .models import Subject, Question, Answer, AnswerImage,Vote

# Allow superusers to manage subjects
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']  # Show subjects in admin panel
    search_fields = ['name']  # Allow searching subjects

# Register other models
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerImage)
admin.site.register(Vote)
