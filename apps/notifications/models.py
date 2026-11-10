from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bloodseekr_notifications",
    )
    blood_request = models.ForeignKey(
        "blood_requests.BloodRequest",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification"

    def __str__(self):
        return self.title
