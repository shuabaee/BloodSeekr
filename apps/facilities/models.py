from django.db import models


class Facility(models.Model):
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(max_length=254)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "facility"
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name
