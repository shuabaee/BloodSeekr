"""Public read API of the profile feature (used by the dashboard and the profile screen)."""
from .models import Profile

# (key, label, hint shown when missing)
CHECKLIST = [
    ('name', 'Full name', 'Add your first and last name.'),
    ('email', 'Email address', 'Needed for account recovery and alerts.'),
    ('phone', 'Phone number', 'Lets requesters reach you after you are accepted.'),
    ('blood_type', 'Blood type', 'Required to be matched with requests.'),
    ('date_of_birth', 'Date of birth', 'Helps facilities confirm eligibility.'),
    ('location', 'Matching location', 'Pin a nearby area so we can find requests close to you.'),
]


def completeness(user):
    """How complete the user's donor profile is: percent plus the list of missing items."""
    profile, _ = Profile.objects.get_or_create(user=user)
    done = {
        'name': bool(user.first_name and user.last_name),
        'email': bool(user.email),
        'phone': bool(profile.phone_number),
        'blood_type': bool(profile.blood_type_id),
        'date_of_birth': bool(profile.date_of_birth),
        'location': bool(profile.location),
    }
    missing = [{'key': k, 'label': label, 'hint': hint} for k, label, hint in CHECKLIST if not done[k]]
    percent = round(100 * (len(CHECKLIST) - len(missing)) / len(CHECKLIST))
    return {'percent': percent, 'missing': missing, 'complete': not missing, 'profile': profile,
            'ready_to_donate': profile.available_to_donate and bool(profile.blood_type_id and profile.location and profile.phone_number)}
