from django.apps import AppConfig


class SharedConfig(AppConfig):
    """Utilities only (locations, widgets, template tags). No models, no migrations."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shared"
    label = "shared"
