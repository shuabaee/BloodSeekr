from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bloodseekr_settings",
    )
    email_notifications = models.BooleanField(default=True)
    emergency_notifications = models.BooleanField(default=True)
    show_donor_profile = models.BooleanField(default=True)
    match_radius_km = models.SmallIntegerField(default=25)

    class Meta:
        db_table = "user_settings"
        verbose_name_plural = "User settings"

    def __str__(self):
        return f"{self.user.username} Settings"
