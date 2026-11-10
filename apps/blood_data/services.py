import re
from django.apps import apps
from django.utils import timezone
from .models import BloodCompatibility
ACTIVE_STATUSES = ('open', 'in_progress')

def normalize_location(value):
    return ' '.join(re.sub(r'[^\w\s]', ' ', value.casefold()).split())

from apps.shared.locations import coordinates, location_matches

def donor_eligible(user, blood_request, check_location=True):
    if not user.is_active or user.pk == blood_request.requester_id:
        return False
    if blood_request.status not in ACTIVE_STATUSES or blood_request.verification_status == 'rejected' or blood_request.needed_date < timezone.localdate():
        return False
    Profile = apps.get_model('profiles','Profile')
    profile = Profile.objects.filter(user=user, available_to_donate=True).first()
    if not profile or not profile.blood_type_id:
        return False
    compatible = BloodCompatibility.objects.filter(donor_blood_type_id=profile.blood_type_id, recipient_blood_type_id=blood_request.required_blood_type_id, is_compatible=True).exists()
    if not compatible:
        return False
    preferences = apps.get_model('user_settings','UserSettings').objects.filter(user=user).first()
    radius = preferences.match_radius_km if preferences else 25
    return not check_location or location_matches(profile.location, blood_request.location, radius)

def matching_requests(user):
    Request = apps.get_model('blood_requests','BloodRequest')
    qs = Request.objects.filter(status__in=ACTIVE_STATUSES, needed_date__gte=timezone.localdate()).exclude(verification_status='rejected').exclude(requester=user).select_related('required_blood_type','facility').order_by('needed_date','-created_at')
    return [item for item in qs if donor_eligible(user, item)]

def matching_donors(blood_request, visible_only=False):
    Profile = apps.get_model('profiles','Profile')
    qs = Profile.objects.filter(available_to_donate=True, user__is_active=True).select_related('user','blood_type','user__bloodseekr_settings')
    if visible_only:
        qs = qs.exclude(user__bloodseekr_settings__show_donor_profile=False)
    return [profile for profile in qs if donor_eligible(profile.user, blood_request)]


# --- Compatibility read API (used by this feature's guide and by other features' templates) ---
def compatibility_map():
    """{donor_code: [recipient_code, ...]} for every compatible pair, ordered by blood type."""
    result = {}
    pairs = BloodCompatibility.objects.filter(is_compatible=True).order_by('donor_blood_type_id', 'recipient_blood_type_id')
    for donor, recipient in pairs.values_list('donor_blood_type_id', 'recipient_blood_type_id'):
        result.setdefault(donor, []).append(recipient)
    return result


def recipients_for(code):
    """Blood types a donor of `code` can give red cells to."""
    return compatibility_map().get(code, [])


def donors_for(code):
    """Blood types that can give red cells to a recipient of `code`."""
    return [donor for donor, recipients in compatibility_map().items() if code in recipients]


def blood_types():
    """All blood types, for pickers and filters."""
    from .models import BloodType
    return BloodType.objects.all()
