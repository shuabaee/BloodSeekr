from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
import logging
from .models import Notification
logger = logging.getLogger(__name__)

def notify(user, blood_request, kind, title, message):
    notice = Notification.objects.create(user=user, blood_request=blood_request, notification_type=kind, title=title, message=message)
    preferences = apps.get_model('user_settings','UserSettings').objects.filter(user=user).first()
    if user.email and preferences and preferences.email_notifications:
        def email():
            try:
                send_mail(title, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception:
                logger.warning('Email delivery failed for notification %s.', notice.pk)
        transaction.on_commit(email)
    return notice

def notify_matches(blood_request):
    from apps.blood_data.services import matching_donors
    for profile in matching_donors(blood_request):
        preferences = apps.get_model('user_settings','UserSettings').objects.filter(user=profile.user).first()
        if blood_request.urgency == 'emergency' and preferences and not preferences.emergency_notifications:
            continue
        notify(profile.user, blood_request, 'matching_request', 'A blood request matches you', f'Request #{blood_request.pk} needs {blood_request.required_blood_type_id} in {blood_request.location}.')


# --- Public read API for other features (e.g. the dashboard) ---
def recent_for(user, limit=4):
    return Notification.objects.filter(user=user).select_related('blood_request').order_by('-created_at')[:limit]


def unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()
