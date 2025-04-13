from django.contrib import admin
from .models import Notes  # Import your model

@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'department', 'semester', 'status', 'uploaded_by', 'uploaded_at')
    list_filter = ('department', 'semester', 'status')
    search_fields = ('title', 'subject', 'tags', 'uploaded_by__username')
 
