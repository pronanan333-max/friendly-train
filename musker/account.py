from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!  Get MEEPING!")
            return redirect('home')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('login')

    return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out. Sorry to Meep You Go...")
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # create inactive user and send activation email
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # build activation token and link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_path = reverse('activate', args=[uid, token])
            activation_link = request.build_absolute_uri(activation_path)

            try:
                subject = 'Musker - Activate your account'
                message = (
                    f'Hi {user.username},\n\n'
                    f'Please click the link below to activate your Musker account:\n{activation_link}\n\n'
                    'If you did not register, please ignore this email.'
                )
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
                recipient_list = [form.cleaned_data.get('email')]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, "Registration successful — check your email to activate your account.")
            except Exception:
                messages.warning(request, "Registered but failed to send activation email.")

            return redirect('home')

    return render(request, 'register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        from django.contrib.auth.models import User
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect('home')
