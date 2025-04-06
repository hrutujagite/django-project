from django.urls import path
from .views import upload_notes, notes_list, pending_notes, approve_note,search_notes

urlpatterns = [
    path('upload/', upload_notes, name='upload_notes'),
    path('my-notes/', notes_list, name='notes_list'),
    path('pending/', pending_notes, name='pending_notes'),
    path('approve/<int:note_id>/', approve_note, name='approve_note'),
    path("search/", search_notes, name="search_notes"),
]
