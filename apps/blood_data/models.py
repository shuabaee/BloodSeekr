from django.db import models


class BloodType(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    abo_group = models.CharField(max_length=2)
    rh_factor = models.CharField(max_length=1)
    display_name = models.CharField(max_length=5, unique=True)

    class Meta:
        db_table = "blood_type"
        ordering = ["code"]

    def __str__(self):
        return self.display_name


class BloodCompatibility(models.Model):
    donor_blood_type = models.ForeignKey(
        BloodType,
        to_field="code",
        db_column="donor_blood_type_code",
        on_delete=models.CASCADE,
        related_name="donor_compatibilities",
    )
    recipient_blood_type = models.ForeignKey(
        BloodType,
        to_field="code",
        db_column="recipient_blood_type_code",
        on_delete=models.CASCADE,
        related_name="recipient_compatibilities",
    )
    pk = models.CompositePrimaryKey("donor_blood_type", "recipient_blood_type")
    is_compatible = models.BooleanField(default=True)

    class Meta:
        db_table = "blood_compatibility"

    def __str__(self):
        return f"{self.donor_blood_type} -> {self.recipient_blood_type}"
