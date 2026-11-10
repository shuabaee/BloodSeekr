from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_defaults(sender, instance, created, raw=False, using='default', **kwargs):
    if created and not raw:
        apps.get_model('profiles', 'Profile').objects.using(using).get_or_create(user=instance)
        apps.get_model('user_settings', 'UserSettings').objects.using(using).get_or_create(user=instance)
