"""Dashboard. It only composes other features through their public services.py APIs."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.blood_data.services import matching_requests
from apps.blood_requests.services import attach_progress, dashboard_for
from apps.donations.services import history_for, summary_for
from apps.notifications.services import recent_for, unread_count
from apps.profile.services import completeness


def greeting():
    hour = timezone.localtime().hour
    return 'Good morning' if hour < 12 else 'Good afternoon' if hour < 18 else 'Good evening'


def attention_items(user, strength, requests_data, matches, unread):
    """What the user should do next, most important first."""
    items = []
    count = requests_data['pending_offer_count']
    if count:
        first = requests_data['pending_offers'][0]
        who = first.donor_user.get_full_name() or first.donor_user.username
        items.append({'icon': 'users', 'tone': 'urgent', 'title': f'{count} donor offer{"s" if count != 1 else ""} waiting for your reply',
                      'text': f'{who} offered to help with request #{first.blood_request_id}.', 'label': 'Review offers',
                      'url': reverse('blood_requests:detail', args=[first.blood_request_id])})
    emergencies = [m for m in matches if m.urgency == 'emergency']
    if emergencies:
        first = emergencies[0]
        items.append({'icon': 'siren', 'tone': 'emergency', 'title': f'{len(emergencies)} emergency request{"s" if len(emergencies) != 1 else ""} match you',
                      'text': f'{first.required_blood_type} needed {first.needed_date:%b %d}. You could help right now.', 'label': 'See request',
                      'url': reverse('blood_requests:detail', args=[first.pk])})
    if not strength['complete']:
        missing = ', '.join(m['label'].lower() for m in strength['missing'][:3])
        items.append({'icon': 'user', 'tone': 'info', 'title': f'Finish your profile ({strength["percent"]}% done)',
                      'text': f'Still missing: {missing}.', 'label': 'Complete profile', 'url': reverse('profile:profile')})
    elif not strength['profile'].available_to_donate:
        items.append({'icon': 'heart', 'tone': 'info', 'title': 'Turn on donor availability',
                      'text': 'You are not receiving matches while unavailable.', 'label': 'Become available', 'url': reverse('profile:profile')})
    if unread:
        items.append({'icon': 'bell', 'tone': 'info', 'title': f'{unread} unread notification{"s" if unread != 1 else ""}',
                      'text': 'Catch up on updates about your requests and offers.', 'label': 'Open', 'url': reverse('notifications:list')})
    return items


@login_required
def home_view(request):
    user = request.user
    strength = completeness(user)
    requests_data = dashboard_for(user)
    matches = matching_requests(user)
    unread = unread_count(user)
    donation = summary_for(user)
    context = {
        'greeting': greeting(),
        'display_name': user.first_name or user.username,
        'profile': strength['profile'],
        'strength': strength,
        'donation': donation,
        'attention': attention_items(user, strength, requests_data, matches, unread),
        'matching_requests': attach_progress(matches[:3]),
        'matching_count': len(matches),
        'recent_notifications': recent_for(user, 4),
        'unread_count_home': unread,
        'donations': history_for(user, 4),
        **requests_data,
    }
    return render(request, 'home/home.html', context)
