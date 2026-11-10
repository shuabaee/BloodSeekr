from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bloodseekr_profile",
    )
    blood_type = models.ForeignKey(
        "blood_data.BloodType",
        to_field="code",
        db_column="blood_type_code",
        on_delete=models.PROTECT,
        related_name="profiles",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=150, blank=True)
    available_to_donate = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "profile"

    def __str__(self):
        return f"{self.user.username} Profile"
