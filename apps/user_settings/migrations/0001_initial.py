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
            name="UserSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email_notifications", models.BooleanField(default=True)),
                ("emergency_notifications", models.BooleanField(default=True)),
                ("show_donor_profile", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="bloodseekr_settings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name_plural": "User settings"},
        ),
    ]
