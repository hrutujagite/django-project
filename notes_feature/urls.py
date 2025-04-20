from django.urls import path
from . import views

app_name = 'notes_feature'

urlpatterns = [
    path('upload/', views.upload_notes, name='upload_notes'),
    path('approve/<int:note_id>/', views.approve_note, name='approve_note'),
    path('reject/<int:note_id>/', views.reject_note, name='reject_note'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('view/<int:note_id>/', views.view_note, name='view_note'),
    path('search/', views.search_notes, name='search_notes'),
    path('my-notes/', views.my_notes, name='my_notes'),
    path('pending-notes/', views.pending_notes, name='pending_notes'),
    path('view-file/<int:note_id>/', views.view_file, name='view_file'),
    path('note/<int:note_id>/reject/', views.reject_note, name='reject_note'),
]
