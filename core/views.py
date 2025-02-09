import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from .forms import SignUpForm

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
    email_regex = r'^[a-zA-Z0-9]+@([a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)\.fcrit\.ac\.in$'
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format. The email must be of the format 'anything@fcrit.ac.in' or 'rollno@branch.fcrit.ac.in'.")
    return email

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
                validate_email(email)

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
    return render(request, 'email_verification_sent.html')
