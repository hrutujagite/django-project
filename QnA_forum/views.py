from django.shortcuts import render, redirect ,get_object_or_404
from .models import Question, Subject,Answer,Vote,AnswerImage
from django.contrib.auth.decorators import login_required
from .forms import AnswerForm
from django.contrib import messages
import json
from django.http import JsonResponse
from django.db import models

@login_required
def question_list(request):
    """Show all questions, filtered by subject if selected"""
    subject_id = request.GET.get('subject')  # Get selected subject from the dropdown
    subjects = Subject.objects.all()  # Get all subjects

    if subject_id:
        questions = Question.objects.filter(subject_id=subject_id).order_by('-created_at')
    else:
        questions = Question.objects.all().order_by('-created_at')

    return render(request, 'QnA_forum/question_list.html', {'questions': questions, 'subjects': subjects, 'selected_subject': subject_id})


@login_required
def ask_question(request):
    """Allow users to ask a new question"""
    if request.method == "POST":
        content = request.POST.get("content")
        subject_name = request.POST.get("subject")

        if content and subject_name:
            # Create or get the subject
            subject, created = Subject.objects.get_or_create(name=subject_name.strip())
            if created:
                messages.success(request, f"New subject '{subject_name}' created successfully!")
            
            # Create the question
            Question.objects.create(content=content, subject=subject, user=request.user)
            messages.success(request, "Your question has been posted successfully!")
            return redirect('QnA_forum:question_list')
        else:
            messages.error(request, "Please provide both a subject and question content.")

    return render(request, 'QnA_forum/ask_question.html')


def question_detail(request, question_id):
    """Display a single question and handle answer submission."""
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all()
    
    # Sort answers by total votes
    sorted_answers = sorted(answers, key=lambda a: a.total_votes(), reverse=True)
    
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user
            answer.save()
            images = request.FILES.getlist('images')

            if len(images) > 3:
                messages.error(request, "You can only upload a maximum of 3 images.")
                return redirect('QnA_forum:question_detail', question_id=question.id)

            for image in images:
                AnswerImage.objects.create(answer=answer, image=image)

            return redirect('QnA_forum:question_detail', question_id=question.id)
    else:
        form = AnswerForm()

    return render(request, 'QnA_forum/question_detail.html', {
        'question': question,
        'answers': sorted_answers,
        'form': form
    })



@login_required
def edit_question(request, question_id):
    """Allow users to edit their own questions"""
    question = get_object_or_404(Question, id=question_id)

    # Ensure only the owner or an admin can edit
    if request.user != question.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this question.")
        return redirect('QnA_forum:question_list')  # Prevent unauthorized edits

    if request.method == "POST":
        content = request.POST.get("content")
        subject_id = request.POST.get("subject")

        if content and subject_id:
            question.content = content
            question.subject = Subject.objects.get(id=subject_id)
            question.save()
            messages.success(request, "Question updated successfully.")
            return redirect('QnA_forum:question_list')  # Redirect to QnA forum after editing

    subjects = Subject.objects.all()
    return render(request, 'QnA_forum/edit_question.html', {'question': question, 'subjects': subjects})


@login_required
def toggle_pin_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if request.user in question.pinned_by.all():
        question.pinned_by.remove(request.user)  # Unpin
    else:
        question.pinned_by.add(request.user)  # Pin

    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirect back

def toggle_report_question(request, question_id):
    """Toggle between reporting and unreporting a question"""
    question = get_object_or_404(Question, id=question_id)

    if request.user in question.reported_by.all():
        question.unreport(request.user)
        messages.success(request, "You have unreported this question.")
    else:
        question.report(request.user)
        messages.success(request, "This question has been reported successfully.")

    return redirect('QnA_forum:question_list')  # Redirect to your question list page

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Only the owner or admin can delete
    if request.user == question.user or request.user.is_superuser:
        question.delete()
        return redirect('QnA_forum:question_list')  # Redirect to the main Q&A page
    else:
        return redirect('QnA_forum:question_detail', question_id=question.id)



@login_required
def upvote_answer(request, answer_id):
    """Allows users to upvote an answer (except their own)."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Prevent the answer author from voting on their own answer
    if answer.user == request.user:
        messages.error(request, "You cannot vote on your own answer.")
        return redirect('QnA_forum:question_detail', question_id=answer.question.id)

    # Check if user already upvoted
    existing_vote = answer.votes.filter(user=request.user, vote_type=1).first()
    if existing_vote:
        existing_vote.delete()  # Remove the upvote if already exists
        messages.success(request, "Upvote removed.")
    else:
        # Remove any existing downvote by the user
        answer.votes.filter(user=request.user, vote_type=-1).delete()
        # Create new upvote
        Vote.objects.create(user=request.user, answer=answer, vote_type=1)
        messages.success(request, "Answer upvoted successfully.")

    return redirect('QnA_forum:question_detail', question_id=answer.question.id)

@login_required
def downvote_answer(request, answer_id):
    """Allows users to downvote an answer (except their own)."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Prevent the answer author from voting on their own answer
    if answer.user == request.user:
        messages.error(request, "You cannot vote on your own answer.")
        return redirect('QnA_forum:question_detail', question_id=answer.question.id)

    # Check if user already downvoted
    existing_vote = answer.votes.filter(user=request.user, vote_type=-1).first()
    if existing_vote:
        existing_vote.delete()  # Remove the downvote if already exists
        messages.success(request, "Downvote removed.")
    else:
        # Remove any existing upvote by the user
        answer.votes.filter(user=request.user, vote_type=1).delete()
        # Create new downvote
        Vote.objects.create(user=request.user, answer=answer, vote_type=-1)
        messages.success(request, "Answer downvoted successfully.")

    return redirect('QnA_forum:question_detail', question_id=answer.question.id)


@login_required
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    # Check if user has permission to edit
    if request.user != answer.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this answer.")
        return redirect('QnA_forum:question_detail', question_id=answer.question.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            answer.content = content
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            if images:
                # Check if adding new images would exceed the limit
                current_image_count = answer.images.count()
                if current_image_count + len(images) > 3:
                    messages.error(request, "You can only have a maximum of 3 images per answer.")
                    return redirect('QnA_forum:edit_answer', answer_id=answer.id)
                
                # Add new images
                for image in images:
                    AnswerImage.objects.create(answer=answer, image=image)
            
            # Handle image deletions
            delete_images = request.POST.getlist('delete_images')
            for image_id in delete_images:
                try:
                    image = AnswerImage.objects.get(id=image_id, answer=answer)
                    image.delete()
                except AnswerImage.DoesNotExist:
                    pass
            
            answer.save()
            messages.success(request, "Answer updated successfully!")
            return redirect('QnA_forum:question_detail', question_id=answer.question.id)
    
    context = {
        'answer': answer,
        'question': answer.question
    }
    return render(request, 'QnA_forum/edit_answer.html', context)

@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question_id = answer.question.id
    
    # Check if user has permission to delete
    if request.user != answer.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete this answer.")
        return redirect('QnA_forum:question_detail', question_id=question_id)
    
    # Delete the answer directly
    answer.delete()
    messages.success(request, "Answer deleted successfully!")
    return redirect('QnA_forum:question_detail', question_id=question_id)

