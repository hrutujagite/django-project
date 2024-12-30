from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage route
    path('login/', views.user_login, name='login'),  # Updated to use the renamed login view
    path('signup/', views.signup, name='signup'),  # Signup route
    path('verify_email/', views.verify_email, name='verify_email'),  # Email verification route
    path('email_verification_sent/', views.email_verification_sent, name='email_verification_sent'),  # Confirmation page after sending verification email
]
