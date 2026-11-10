from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profile"
    # Preserve the original Django app label so the existing Supabase
    # profiles_profile table and migration history continue to work.
    label = "profiles"

    def ready(self):
        from . import signals  # noqa: F401
