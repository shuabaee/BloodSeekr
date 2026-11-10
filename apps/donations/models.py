from django.db import models


class DonationRecord(models.Model):
    donor_response = models.OneToOneField(
        "blood_requests.DonorResponse",
        on_delete=models.CASCADE,
        related_name="donation_record",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="donation_records",
    )
    donation_date = models.DateField()
    units_donated = models.DecimalField(max_digits=4, decimal_places=2)
    screening_status = models.CharField(max_length=20)
    donation_status = models.CharField(max_length=20)

    class Meta:
        db_table = "donation_record"

    def __str__(self):
        return f"Donation #{self.pk} - {self.donation_date}"
