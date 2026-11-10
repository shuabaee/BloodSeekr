from django.conf import settings
from django.db import models


class BloodRequest(models.Model):
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_requests",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        related_name="blood_requests",
        null=True,
        blank=True,
    )
    required_blood_type = models.ForeignKey(
        "blood_data.BloodType",
        to_field="code",
        db_column="required_blood_type_code",
        on_delete=models.PROTECT,
        related_name="blood_requests",
    )
    patient_name = models.CharField(max_length=150)
    units_needed = models.SmallIntegerField()
    urgency = models.CharField(max_length=20)
    needed_date = models.DateField()
    location = models.CharField(max_length=255)
    verification_status = models.CharField(max_length=20)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blood_request"

    def __str__(self):
        return f"Blood request #{self.pk} - {self.patient_name}"


class RequestAttachment(models.Model):
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_request_attachments",
    )
    document_type = models.CharField(max_length=50)
    file_url = models.CharField(max_length=500)
    verification_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "request_attachment"

    def __str__(self):
        return f"Attachment #{self.pk} for request #{self.blood_request_id}"


class DonorResponse(models.Model):
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="donor_responses",
    )
    donor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donor_responses",
    )
    response_status = models.CharField(max_length=20)
    responded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "donor_response"
        constraints = [
            models.UniqueConstraint(
                fields=["blood_request", "donor_user"],
                name="uq_donor_response_request_donor",
            )
        ]

    def __str__(self):
        return f"{self.donor_user} -> request #{self.blood_request_id}"
