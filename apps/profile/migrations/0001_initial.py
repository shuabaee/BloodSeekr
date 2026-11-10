from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(blank=True, max_length=20)),
                ("blood_type", models.CharField(blank=True, choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")], max_length=3)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=150)),
                ("available_to_donate", models.BooleanField(default=False)),
                ("last_donation_date", models.DateField(blank=True, null=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="bloodseekr_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
