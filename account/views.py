from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from musker.forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User


def login_user(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ("You Have Been Logged In"))
			return redirect('home')
		else:
			messages.success(request, ("There Was An Error Logging In, Try Again..."))
			return redirect('login')
	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You Have Been Logged Out..."))
	return redirect('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
					user = form.save(commit=False)
					user.is_active = False
					user.save()

					# Send activation email
					subject = 'Activate Your Musker Account'
					uid = urlsafe_base64_encode(force_bytes(user.pk))
					token = default_token_generator.make_token(user)
					host = request.get_host()
					activation_link = f"http://{host}/activate/{uid}/{token}/"
					message = render_to_string('activation_email.txt', {
						'user': user,
						'activation_link': activation_link,
					})
					from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost')
					send_mail(subject, message, from_email, [user.email], fail_silently=False)

					return render(request, 'activation_sent.html', {'email': user.email})
	else:
		form = SignUpForm()

	return render(request, 'register.html', {'form': form})


def activate_account(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception:
		user = None

	if user is not None and default_token_generator.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		return render(request, 'activation_complete.html')
	else:
		return render(request, 'activation_invalid.html')
