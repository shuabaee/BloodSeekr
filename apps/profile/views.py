from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from apps.donations.services import summary_for as donation_summary

from .forms import ProfileForm, UserProfileForm
from .models import Profile
from .services import completeness


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                if "blood_type" in profile_form.changed_data:
                    profile_form.instance.is_verified = False
                profile_form.save()
            messages.success(request, "Profile saved. Your matches are being refreshed with the new details.")
            return redirect("profile:profile")
        messages.error(request, "Some fields need your attention. Please review the form below.")
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        "profile/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
            "strength": completeness(request.user),
            "donation": donation_summary(request.user),
        },
    )
