"""Public read API of the donations feature. Other features call these functions
instead of touching DonationRecord directly."""
import datetime as dt
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import DonationRecord

# Whole-blood donors are normally asked to wait about 8 weeks (56 days) between donations.
# This is informational guidance only; the collecting facility decides eligibility.
WAIT_DAYS = 56
LIVES_PER_DONATION = 3  # "one donation can help up to three people" (an upper estimate)


def records_for(user, role='all'):
    """Donation records the user took part in. role: 'donor', 'requester' or 'all'."""
    donor = Q(donor_response__donor_user=user)
    requester = Q(donor_response__blood_request__requester=user)
    condition = donor if role == 'donor' else requester if role == 'requester' else donor | requester
    return (DonationRecord.objects.filter(condition)
            .select_related('facility', 'donor_response__donor_user', 'donor_response__blood_request')
            .order_by('-donation_date', '-pk'))


def history_for(user, limit=4):
    return records_for(user, 'donor')[:limit]


def summary_for(user):
    """Totals for the user's own completed donations plus their next eligible date."""
    done = DonationRecord.objects.filter(donor_response__donor_user=user, donation_status='completed')
    totals = done.aggregate(count=Count('pk'), units=Sum('units_donated'))
    last = done.order_by('-donation_date').values_list('donation_date', flat=True).first()
    next_date = last + dt.timedelta(days=WAIT_DAYS) if last else None
    today = timezone.localdate()
    scheduled = DonationRecord.objects.filter(donor_response__donor_user=user, donation_status='scheduled').count()
    return {
        'completed': totals['count'] or 0,
        'units': totals['units'] or Decimal('0'),
        'lives': (totals['count'] or 0) * LIVES_PER_DONATION,
        'last_date': last,
        'next_eligible': next_date,
        'can_donate_now': next_date is None or next_date <= today,
        'days_left': max((next_date - today).days, 0) if next_date else 0,
        'scheduled': scheduled,
    }
