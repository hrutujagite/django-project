from django.urls import path
from django.urls import path, include 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage route
    path('login/', views.user_login, name='login'),  # Updated to use the renamed login view
    path('signup/', views.signup, name='signup'),  # Signup route
    path('verify_email/', views.verify_email, name='verify_email'),  # Email verification route
    path('email_verification_sent/', views.email_verification_sent, name='email_verification_sent'),
    path("profile/", views.profile_view, name="profile"),
    path('update-profile/', views.update_profile, name="update_profile"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.change_password, name='change_password'), 
    path('notes/', include('notes_feature.urls')),
 
]