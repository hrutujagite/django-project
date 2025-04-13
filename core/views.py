import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from .forms import *
from .models import Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from  QnA_forum.models import Question 
from notes_feature.models import Notes
from django.contrib.auth import update_session_auth_hash# Assuming questions are stored here
# Initialize the signer for generating tokens
signer = Signer()

# View for homepage
def homepage(request):
    return render(request, 'homepage.html')

# View for login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and redirect to the homepage
            login(request, user)
            return redirect('homepage')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.error(request, "Account does not exist. Please sign up.")

    email_verified = request.session.pop('email_verified', False)
    return render(request, 'login.html', {'email_verified': email_verified})

# View for email verification
def verify_email(request):
    token = request.GET.get('token')
    if token:
        try:
            user_id_from_token = signer.unsign(token)
            user = User.objects.get(id=user_id_from_token)

            user.is_active = True
            user.save()
            request.session['email_verified'] = True
            return redirect('login')

        except (ValidationError, User.DoesNotExist):
            messages.error(request, "Invalid verification link.")
            return redirect('homepage')
    else:
        messages.error(request, "No verification token provided.")
        return redirect('homepage')

# Function to validate the email format
def validate_email(email):
    STUDENT_REGEX = r'^[0-9]{7}@comp\.fcrit\.ac\.in$'
    FACULTY_REGEX = r'^[a-zA-Z]+(\.[a-zA-Z]+)*@fcrit\.ac\.in$'


    if re.match(STUDENT_REGEX, email):
        return email, "student"
    elif re.match(FACULTY_REGEX, email):
        return email, "teacher"
    else:
        raise ValidationError("Invalid email format. Please use a valid student or faculty email.")




# Signup view to handle user registration and email verification
def signup(request):
    if request.method == 'POST':
        print(request.POST) 
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Extract data from cleaned data
            first_name = form.cleaned_data.get('first_name')  # Added first name
            last_name = form.cleaned_data.get('last_name')    # Added last name
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                # Validate the email format
                email, role = validate_email(email)

                # Create the user in the database but keep it inactive initially
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password,
                    first_name=first_name,  # Save first name
                    last_name=last_name     # Save last name
                )
                user.is_active = False
                user.save()
                if not Profile.objects.filter(user=user).exists():
                  Profile.objects.create(user=user, role=role)


                # Generate the signed token for verification
                token = signer.sign(user.pk)

                # Create the verification link
                verification_link = request.build_absolute_uri(
                    reverse('verify_email') + f"?token={token}"
                )

                # Send verification email
                send_mail(
                    'Please Verify Your Email',
                    f'Click the following link to verify your email: {verification_link}',
                    'notenookteam@gmail.com',  # Sender email
                    [email],
                    fail_silently=False,
                )

                # Success message to inform the user
                messages.success(request, "Account created successfully! Please verify your email.")
                return redirect('email_verification_sent')

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

# View for email verification sent confirmation page
def email_verification_sent(request):
    return render(request, 'homepage.html')



@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    user_form = UserEditForm(instance=user)
    password_form = PasswordChangeForm(user)
    if request.method == 'POST':
        if 'update_profile' in request.POST:  # Handle edit profile form
            user_form = UserEditForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('profile')
            else :
               messages.error(request, "Error updating profile. Please correct the errors below.")
               print(user_form.errors)  
        elif 'change_password' in request.POST:  # Handle password change form
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()  # Save the new password
                update_session_auth_hash(request, user)  # Keep user logged in after password change
                messages.success(request, "Your password has been updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Error changing password. Please correct the errors below.")

    else:
        user_form = UserEditForm(instance=user)
        password_form = PasswordChangeForm(user)
   
    context = {
        "profile": profile,
        "user_form": user_form, 
        "password_form": password_form,

    }
    if profile.role == 'student':
        context.update({
            "asked_questions": Question.objects.filter(user=user),
            "pinned_questions": Question.objects.filter(pinned_by=user),
            "uploaded_notes": Notes.objects.filter(uploaded_by=user,status='approved'),  # Uncomment if Note model exists
            "notes_pending_for_approval": Notes.objects.filter(uploaded_by=user, status='pending'),  # Uncomment if Note model exists
        })
    elif profile.role == 'teacher':
        context.update({
            "pinned_questions": Question.objects.filter(pinned_by=user),
            "uploaded_notes": Notes.objects.filter(uploaded_by=user),  # Uncomment if Note model exists
            "notes_for_approval": Notes.objects.filter(status='pending'),  # Uncomment if Note model exists
        })

    return render(request, "core/profile.html", context)




def update_profile(request):
    user = request.user
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Profile updated successfully!")
        
        # Check if both forms are valid and redirect back to the profile page
            return redirect("profile")

    else:
        user_form = UserEditForm(instance=user,user=user)

    return render(request, "core/profile.html", {
        "user_form": user_form,
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            return JsonResponse({"status": "success", "message": "Password changed successfully."})
        else:
            return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "error", "message": "Invalid request."})


