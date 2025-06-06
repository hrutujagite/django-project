import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notes
from .forms import NotesUploadForm
from django.db.models import Q  
from django.http import JsonResponse
from django.template.loader import render_to_string
import re
from django.db.models import Case, When, Value, IntegerField, F, FloatField
from django.db.models.functions import Length
from django.utils.http import quote as urlquote
import os
from mimetypes import guess_type
from QnA_forum.models import Question  # Add this import
import io
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# Google Drive setup
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credentials', 'notenook key imp.json')
FOLDER_ID = '1sR0i7uqeR7n9n-dH2BLTkWYAAP3diGEQ'  
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

logger = logging.getLogger(__name__)

def is_teacher_or_admin(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'teacher')

@login_required
def upload_notes(request):
    if request.method == "POST":
        form = NotesUploadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user

            # ✅ Upload to Google Drive
            uploaded_file = request.FILES['file']
            filename = uploaded_file.name
            mimetype = uploaded_file.content_type

            file_stream = io.BytesIO(uploaded_file.read())

            file_metadata = {
                'name': filename,
                'parents': [FOLDER_ID],
            }
            media = MediaIoBaseUpload(file_stream, mimetype=mimetype)

            uploaded = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            drive_service.permissions().create(
    fileId=uploaded['id'],
    body={
        'type': 'anyone',       # ← Allows anyone with the link
        'role': 'reader'        # ← Read-only permission
    }
).execute()

            drive_link = uploaded.get('webViewLink')
            note.drive_url = drive_link  # assumes you have a field in your model called `drive_url`

            # ✅ Set status based on user role
            if hasattr(request.user, 'profile') and request.user.profile.role == 'teacher':
                note.status = 'approved'
                messages.success(request, "Note uploaded and automatically approved.")
            else:
                note.status = 'pending'
                messages.success(request, "Note uploaded successfully and is pending approval.")

            note.save()

            return render(request, "notes_feature/upload_notes.html", {
                'form': NotesUploadForm(),
                'departments': NotesUploadForm.DEPARTMENT_CHOICES,
                'semesters': NotesUploadForm.SEMESTER_CHOICES,
            })
        else:
            messages.error(request, "❌ Error: Please correct the form errors.")
    else:
        form = NotesUploadForm()

    context = {
        'form': form,
        'departments': NotesUploadForm.DEPARTMENT_CHOICES,
        'semesters': NotesUploadForm.SEMESTER_CHOICES,
    }
    return render(request, "notes_feature/upload_notes.html", context)

@login_required
def approve_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)

    if is_teacher_or_admin(request.user):
        note.status = 'approved'
        note.save()
        return JsonResponse({
            'status': 'success',
            'message': f"✅ '{note.title}' has been approved.",
            'note_id': note_id
        })

    return JsonResponse({
        'status': 'error',
        'message': "❌ You are not allowed to approve notes."
    }, status=403)

@login_required
def reject_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)
    if is_teacher_or_admin(request.user):
        note.status = 'rejected'
        note.save()
        return JsonResponse({
            'status': 'success',
            'message': f'Note "{note.title}" has been rejected.',
            'note_id': note_id
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to reject notes.'
        }, status=403)

@login_required
def pending_notes(request):
    if not is_teacher_or_admin(request.user):
        return HttpResponseForbidden("❌ You are not allowed to view this page.")

    notes = Notes.objects.filter(status='pending')
    return render(request, 'notes_feature/pending_notes.html', {'notes': notes})

@login_required
def search_notes(request):
    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "")
    semester = request.GET.get("semester", "")
    sort = request.GET.get("sort", "relevance")

    notes = Notes.objects.filter(status="approved")

    if query:
        # Calculate match percentage based on multiple factors
        notes = notes.annotate(
            match_score=Case(
                # Exact matches (100%)
                When(title__iexact=query, then=Value(100)),
                When(subject__iexact=query, then=Value(90)),
                
                # Contains matches (partial scores)
                When(title__icontains=query, then=Value(75)),
                When(subject__icontains=query, then=Value(60)),
                When(tags__icontains=query, then=Value(40)),
                
                default=Value(0),
                output_field=FloatField(),
            )
        )

        # Filter for any matches
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()

        if sort == "relevance":
            notes = notes.order_by('-match_score', '-uploaded_at')
    else:
        # If no query, all notes get 100% match but don't show the score
        notes = notes.annotate(match_score=Value(100, output_field=FloatField()))

    if department:
        notes = notes.filter(department=department)

    if semester:
        notes = notes.filter(semester=semester)

    # Latest always sorts by date
    if sort == "latest":
        notes = notes.order_by('-uploaded_at')

    context = {
        "notes": notes,
        "query": query,
        "selected_dept": department,
        "selected_sem": semester,
        "departments": Notes.DEPARTMENT_CHOICES,
        "semesters": Notes.SEMESTER_CHOICES,
        "current_sort": sort,
        "show_match_score": bool(query and sort == "relevance")
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("notes_feature/partials/search_results.html", context)
        return JsonResponse({"html": html})

    return render(request, "notes_feature/search_notes.html", context)

@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Notes, id=note_id)
    if note.status != 'approved' and not (request.user == note.uploaded_by or is_teacher_or_admin(request.user)):
        return HttpResponseForbidden("❌ You are not allowed to view this note.")
    
    context = {
        'note': note,
    }
    return render(request, 'notes_feature/note_detail.html', context)

@login_required
def view_file(request, note_id):
    note = get_object_or_404(Notes, id=note_id)

    # Restrict access for unapproved notes
    if note.status != 'approved' and not (request.user == note.uploaded_by or is_teacher_or_admin(request.user)):
        return HttpResponseForbidden("❌ You are not allowed to view this note.")

    # If stored on Google Drive and note has a preview URL
    if note.drive_url:  # Assuming you saved it during upload
        # Example format: https://drive.google.com/file/d/<file_id>/preview
        return redirect(note.drive_url)

    # If stored locally
    file_path = note.file.path
    content_type, _ = guess_type(file_path)

    if not content_type:
        content_type = 'application/octet-stream'

    # Serve PDF or image inline
    if file_path.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{urlquote(os.path.basename(file_path))}"'
        return response

    # For all other files, serve as attachment
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{urlquote(os.path.basename(file_path))}"'
    return response


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)

    if request.user == note.uploaded_by or is_teacher_or_admin(request.user):
        note.delete()
        messages.success(request, f"🗑️ '{note.title}' has been deleted.")
        return redirect('notes_feature:notes_list')

    return HttpResponseForbidden("❌ You are not allowed to delete this note.")

@login_required
def view_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)
    if note.status != 'approved' and not (request.user == note.uploaded_by or is_teacher_or_admin(request.user)):
        return HttpResponseForbidden("❌ You are not allowed to view this note.")
    
    context = {
        'note': note,
    }
    return render(request, 'notes_feature/note_detail.html', context)

@login_required
def my_notes(request):
    notes = Notes.objects.filter(uploaded_by=request.user)
    context = {
        'notes': notes,
        'total_count': notes.count(),
        'pending_count': notes.filter(status='pending').count(),
        'approved_count': notes.filter(status='approved').count(),
        'rejected_count': notes.filter(status='rejected').count(),
    }
    return render(request, 'notes_feature/notes_list.html', context)