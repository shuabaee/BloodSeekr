from django.contrib import admin

from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "email_notifications",
        "emergency_notifications",
        "show_donor_profile",
        "match_radius_km",
    )
    search_fields = ("user__username", "user__email")
