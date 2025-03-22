from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,)
    bio = models.TextField(blank=True, null=True)  # Optional bio
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        if email.endswith("@comp.fcrit.ac.in") and email[:-17].isdigit():  
            role = "student"
        elif email.endswith("@fcrit.ac.in"):  
            role = "teacher"
        else:
            role = "student"  # Default role

        Profile.objects.get_or_create(user=instance, role=role)



