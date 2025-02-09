from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    """Model to store subjects (Only superusers can add/edit)"""
    name = models.CharField(max_length=100, unique=True)  # Unique subject name

    def __str__(self):
        return self.name

class Question(models.Model):
    """Model to store questions posted by users"""
    content = models.TextField()  # ✅ Single field for asking question
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Link to Subject model
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who asked the question
    created_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)

    def __str__(self):
        return f"Question by {self.user.username} on {self.subject.name}"

    def can_edit(self, user):
        """Check if the user can edit this question"""
        return user == self.user or user.is_superuser

    def can_delete(self, user):
        """Check if the user can delete this question"""
        return user == self.user or user.is_superuser

    def get_sorted_answers(self):
        return self.answers.annotate(vote_count=models.Sum('votes__vote_type')).order_by('-vote_count', '-created_at')

class Answer(models.Model):
    """Model to store answers linked to a question"""
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who answered
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    
    def upvote_count(self):
        """Returns the total number of upvotes for this answer."""
        return self.votes.filter(vote_type=1).count()

    def downvote_count(self):
        """Returns the total number of downvotes for this answer."""
        return self.votes.filter(vote_type=-1).count()

    def total_votes(self):
        """Returns the total score (upvotes - downvotes)."""
        return self.upvote_count() - self.downvote_count()
    def __str__(self):
        return f"Answer by {self.user.username} on {self.question.subject.name}"

class AnswerImage(models.Model):
    """Model to store multiple images linked to an answer"""
    answer = models.ForeignKey(Answer, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='answer_images/')  # Store images in 'media/answer_images/'

    def __str__(self):
        return f"Image for Answer {self.answer.id}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="votes", on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=[(1, "Upvote"), (-1, "Downvote")])

    class Meta:
        unique_together = ('user', 'answer') 