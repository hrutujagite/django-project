from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Display user and role in the admin panel
    search_fields = ('user__username', 'role')  # Add search functionality



