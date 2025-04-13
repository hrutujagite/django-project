from django.db import models
from django.contrib.auth.models import User

class Notes(models.Model):
    # Status choices for review process
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    # Department choices; adjust as needed
    DEPARTMENT_CHOICES = [
        ('COMMON', 'Common (First Year)'),
        ('CS', 'Computer Science'),
        ('ME', 'Mechanical Engineering'),
        ('EE', 'Electrical Engineering'),
        # Add more departments as necessary
    ]
    
    # Semester choices (1 through 8)
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    # Core fields
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    subject = models.CharField(max_length=255)
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Enter comma-separated tags (e.g., calculus, integration)"
    )
    description = models.TextField()
    file = models.FileField(upload_to='notes/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.uploaded_by.username}"


