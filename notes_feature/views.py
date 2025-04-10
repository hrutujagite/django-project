import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notes
from .forms import NotesUploadForm
from django.db.models import Q  
from django.http import JsonResponse
from django.template.loader import render_to_string
import re

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

        # ✅ Set status based on user role
        if hasattr(request.user, 'profile') and request.user.profile.role == 'teacher':
            note.status = 'approved'
            messages.success(request, "✅ Note uploaded and automatically approved.")
        else:
            note.status = 'pending'
            messages.success(request, "✅ Note uploaded successfully and is pending approval.")

        note.save()
        return redirect('notes_list')
    else:
        messages.error(request, "❌ Error: Please correct the form errors.")
 else:
    form = NotesUploadForm()

 return render(request, "notes_feature/upload_notes.html", {"form": form})


@login_required
def approve_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)

    if is_teacher_or_admin(request.user):
        note.status = 'approved'
        note.save()
        messages.success(request, f"✅ '{note.title}' has been approved.")
        return redirect('pending_notes')

    return HttpResponseForbidden("❌ You are not allowed to approve notes.")

@login_required
def notes_list(request):
    user_notes = Notes.objects.filter(uploaded_by=request.user)
    return render(request, 'notes_feature/notes_list.html', {'notes': user_notes})

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

    notes = Notes.objects.filter(status="approved")

    if query:
        flexible_query = re.sub(r'(\w)', r'\1%', query)
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(tags__icontains=query) |
            Q(title__icontains=flexible_query)
        ).distinct()

    if department:
        notes = notes.filter(department=department)

    if semester:
        notes = notes.filter(semester=semester)

    context = {
        "notes": notes,
        "query": query,
        "selected_department": department,
        "selected_semester": semester,
        "semesters": range(1, 9),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("notes_feature/partials/search_results.html", context)
        return JsonResponse({"html": html})

    return render(request, "notes_feature/search_notes.html", context)