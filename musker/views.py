from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Profile, Meep
from .forms import MeepForm, SignUpForm, ProfilePicForm
from django.db.models import Q

import stripe

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import Donation

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    meeps = Meep.objects.all().order_by("-created_at")

    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            meep = form.save(commit=False)
            meep.user = request.user
            meep.save()
            messages.success(request, "Your Meep Has Been Posted!")
            return redirect("home")

        return render(request, "home.html", {"meeps": meeps, "form": form})

    return render(request, "home.html", {"meeps": meeps})


def profile_list(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.")
        return redirect("home")

    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "profile_list.html", {"profiles": profiles})


def follow(request, pk):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user_id=pk)
        request.user.profile.follows.add(profile)
        messages.success(request, f"You followed {profile.user.username}")
        return redirect(request.META.get("HTTP_REFERER", "home"))

    messages.error(request, "You must be logged in.")
    return redirect("home")


def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user_id=pk)
        request.user.profile.follows.remove(profile)
        messages.success(request, f"You unfollowed {profile.user.username}")
        return redirect(request.META.get("HTTP_REFERER", "home"))

    messages.error(request, "You must be logged in.")
    return redirect("home")


def profile(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.")
        return redirect("home")

    profile = get_object_or_404(Profile, user_id=pk)
    meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

    if request.method == "POST":
        action = request.POST.get("follow")
        if action == "follow":
            request.user.profile.follows.add(profile)
        elif action == "unfollow":
            request.user.profile.follows.remove(profile)

    return render(request, "profile.html", {"profile": profile, "meeps": meeps})


def followers(request, pk):
    if request.user.id != pk:
        messages.error(request, "Access denied.")
        return redirect("home")

    profile = get_object_or_404(Profile, user_id=pk)
    return render(request, "followers.html", {"profiles": profile})


def follows(request, pk):
    if request.user.id != pk:
        messages.error(request, "Access denied.")
        return redirect("home")

    profile = get_object_or_404(Profile, user_id=pk)
    return render(request, "follows.html", {"profiles": profile})


def update_user(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.")
        return redirect("home")

    user = request.user
    profile = user.profile

    user_form = SignUpForm(request.POST or None, request.FILES or None, instance=user)
    profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile)

    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        login(request, user)
        messages.success(request, "Profile updated!")
        return redirect("home")

    return render(
        request,
        "update_user.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def meep_like(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in.")
        return redirect("home")

    meep = get_object_or_404(Meep, id=pk)

    if meep.likes.filter(id=request.user.id).exists():
        meep.likes.remove(request.user)
    else:
        meep.likes.add(request.user)

    return redirect(request.META.get("HTTP_REFERER", "home"))


def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    return render(request, "show_meep.html", {"meep": meep})

def delete_meep(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please login.")
        return redirect("home")

    meep = get_object_or_404(Meep, id=pk)

    if request.user != meep.user:
        messages.error(request, "You don't own this meep.")
        return redirect("home")

    meep.delete()
    messages.success(request, "Meep deleted.")
    return redirect(request.META.get("HTTP_REFERER", "home"))

def edit_meep(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please login.")
        return redirect("home")

    meep = get_object_or_404(Meep, id=pk)

    if request.user != meep.user:
        messages.error(request, "You don't own this meep.")
        return redirect("home")

    form = MeepForm(request.POST or None, instance=meep)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Meep updated!")
        return redirect("home")

    return render(request, "edit_meep.html", {"form": form, "meep": meep})

def search(request):
    if request.method == "POST":
        query = request.POST.get("search")
        results = Meep.objects.filter(body__icontains=query)
        return render(request, "search.html", {"search": query, "searched": results})

    return render(request, "search.html")


def donate_view(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "thb",
                    "product_data": {
                        "name": "Support Donation ☕",
                    },
                    "unit_amount": amount * 100,  # บาท → สตางค์
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri("/donate/success/"),
            cancel_url=request.build_absolute_uri("/donate/"),
        )

        Donation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            stripe_session_id=session.id,
			status="pending"
        )

        return redirect(session.url)

    return render(request, "donate.html", {
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })

def donate_success(request):
    messages.success(request, "💙 Thank you for your support!")
    return render(request, "donate_success.html")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # ✅ PAYMENT SUCCESS
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        try:
            donation = Donation.objects.get(
                stripe_session_id=session["id"]
            )
            donation.status = "paid"
            donation.payment_intent = session["payment_intent"]
            donation.save()
        except Donation.DoesNotExist:
            pass

    # ❌ PAYMENT FAILED
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        Donation.objects.filter(
            payment_intent=intent["id"]
        ).update(status="failed")

    return HttpResponse(status=200)
