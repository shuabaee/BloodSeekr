from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import UserSettingsForm
from .models import UserSettings


@login_required
def settings_view(request):
    preferences, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved.")
            return redirect("user_settings:settings")
        messages.error(request, "Please check the highlighted setting.")
    else:
        form = UserSettingsForm(instance=preferences)

    return render(request, "user_settings/settings.html", {"form": form})


class ChangePasswordView(SuccessMessageMixin, auth_views.PasswordChangeView):
    """Change password while signed in (Django keeps the session valid afterwards)."""

    template_name = "user_settings/password_change.html"
    success_url = reverse_lazy("user_settings:settings")
    success_message = "Your password was changed."
