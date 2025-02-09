from django.shortcuts import render, redirect ,get_object_or_404
from .models import Question, Subject,Answer,Vote,AnswerImage
from django.contrib.auth.decorators import login_required
from .forms import AnswerForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
        subject_id = request.POST.get("subject")

        if content and subject_id:
            subject = Subject.objects.get(id=subject_id)  # Get selected subject
            Question.objects.create(content=content, subject=subject, user=request.user)
            return redirect('question_list')

    subjects = Subject.objects.all()  # Get all subjects for the dropdown
    return render(request, 'QnA_forum/ask_question.html', {'subjects': subjects})


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'QnA_forum/question_list.html', {'question': question})


@login_required
def edit_question(request, question_id):
    """Allow users to edit their own questions"""
    question = get_object_or_404(Question, id=question_id)

    # Ensure only the owner or an admin can edit
    if request.user != question.user and not request.user.is_superuser:
        return redirect('question_list')  # Prevent unauthorized edits

    if request.method == "POST":
        content = request.POST.get("content")
        subject_id = request.POST.get("subject")

        if content and subject_id:
            question.content = content
            question.subject = Subject.objects.get(id=subject_id)
            question.save()
            return redirect('question_list')  # Redirect after editing

    subjects = Subject.objects.all()
    return render(request, 'QnA_forum/ask_question.html', {'question': question, 'subjects': subjects})

@login_required
def question_detail(request, question_id):
    """Display a single question and handle answer submission."""
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all()  # Get all answers related to this question

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user  # Assign current user as the answerer
            answer.save()
            images = request.FILES.getlist('images')  
            

            # ✅ Backend Validation: Reject more than 3 images
            if len(images) > 3:
                messages.error(request, "You can only upload a maximum of 3 images.")
                return redirect('question_detail', question_id=question.id)

            # ✅ Save images if within limit
            for image in images:
                AnswerImage.objects.create(answer=answer, image=image)

            return redirect('question_detail', question_id=question.id)

    else:
        form = AnswerForm()

    return render(request, 'QnA_forum/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form
    })

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Only the owner or admin can delete
    if request.user == question.user or request.user.is_superuser:
        question.delete()
        return redirect('question_list')  # Redirect to the main Q&A page
    else:
        return redirect('question_detail', question_id=question.id)



@login_required
def upvote_answer(request, answer_id):
    """Allows users to upvote an answer."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Remove any existing downvote by the user
    answer.votes.filter(user=request.user, vote_type=-1).delete()

    # Check if user already upvoted
    existing_vote = answer.votes.filter(user=request.user, vote_type=1).first()
    if existing_vote:
        existing_vote.delete()  # Remove the upvote if already exists
    else:
        Vote.objects.create(user=request.user, answer=answer, vote_type=1)

    return redirect('question_detail', question_id=answer.question.id)

@login_required
def downvote_answer(request, answer_id):
    """Allows users to downvote an answer."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Remove any existing upvote by the user
    answer.votes.filter(user=request.user, vote_type=1).delete()

    # Check if user already downvoted
    existing_vote = answer.votes.filter(user=request.user, vote_type=-1).first()
    if existing_vote:
        existing_vote.delete()  # Remove the downvote if already exists
    else:
        Vote.objects.create(user=request.user, answer=answer, vote_type=-1)

    return redirect('question_detail', question_id=answer.question.id)

@login_required
def edit_answer(request, answer_id):
    """Allows users to edit their own answers."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Check if the logged-in user is the answer owner
    if request.user != answer.user and not request.user.is_superuser:
        return redirect('question_detail', question_id=answer.question.id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect('question_detail', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)

    return render(request, 'edit_answer.html', {'form': form, 'answer': answer})

@login_required
def delete_answer(request, answer_id):
    """Allows users to delete their own answers."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Check if the logged-in user is the answer owner or an admin
    if request.user == answer.user or request.user.is_superuser:
        answer.delete()

    return redirect('question_detail', question_id=answer.question.id)
