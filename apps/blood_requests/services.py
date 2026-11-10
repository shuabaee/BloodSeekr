# --- Read API shared with other features (dashboard, facilities) ---
from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.blood_data.services import ACTIVE_STATUSES, donor_eligible
from .models import BloodRequest, DonorResponse


def can_view(user, item):
    """A request is visible to staff, its owner, donors who responded and eligible donors."""
    return user.is_staff or item.requester_id == user.pk or item.donor_responses.filter(donor_user=user).exists() or donor_eligible(user, item)


def active_requests():
    """Open requests that can still receive help."""
    return (BloodRequest.objects.filter(status__in=ACTIVE_STATUSES, needed_date__gte=timezone.localdate())
            .exclude(verification_status='rejected'))


def attach_progress(items):
    """Annotate each request with units_done / progress_pct using a single query."""
    items = list(items)
    if not items:
        return items
    rows = (DonorResponse.objects.filter(blood_request__in=items, donation_record__donation_status='completed', donation_record__screening_status='passed')
            .values('blood_request_id').annotate(total=Sum('donation_record__units_donated')))
    done = {row['blood_request_id']: row['total'] or 0 for row in rows}
    for item in items:
        item.units_done = done.get(item.pk, 0)
        item.progress_pct = min(100, round(100 * float(item.units_done) / item.units_needed)) if item.units_needed else 0
    return items


def pending_offers_for(user):
    """Offers from donors waiting for this user's decision, on their still-active requests."""
    return (DonorResponse.objects.filter(blood_request__requester=user, blood_request__status__in=ACTIVE_STATUSES, response_status='pending')
            .select_related('blood_request', 'donor_user').order_by('-responded_at'))


def dashboard_for(user, limit=3):
    """Everything the dashboard needs from this feature in one call."""
    mine = BloodRequest.objects.filter(requester=user).select_related('required_blood_type', 'facility').order_by('-created_at')
    open_mine = mine.filter(status__in=ACTIVE_STATUSES)
    return {
        'my_requests': attach_progress(mine[:limit]),
        'my_request_count': mine.count(),
        'my_open_count': open_mine.count(),
        'active_count': active_requests().count(),
        'pending_offers': list(pending_offers_for(user)[:limit]),
        'pending_offer_count': pending_offers_for(user).count(),
        'responses_count': DonorResponse.objects.filter(donor_user=user).count(),
    }


def timeline(item, responses):
    """Progress steps shown on the request page: (label, state, hint). state: done | current | todo | failed."""
    statuses = [r.response_status for r in responses]
    accepted = any(s in ('accepted', 'completed') for s in statuses)
    donated = any(s == 'completed' for s in statuses)
    closed_fail = item.status == 'cancelled'
    steps = [
        ('Request posted', 'done', 'Visible to matching donors'),
        ('Donor accepted', 'done' if accepted else 'todo', 'A donor offered and you accepted'),
        ('Donation recorded', 'done' if donated else 'todo', 'Completed after screening'),
        ('Cancelled' if closed_fail else 'Fulfilled', 'failed' if closed_fail else ('done' if item.status == 'fulfilled' else 'todo'), 'This request was cancelled' if closed_fail else 'Requested units reached'),
    ]
    # first unfinished step is the "current" one
    if not closed_fail:
        for i, (label, state, hint) in enumerate(steps):
            if state == 'todo':
                steps[i] = (label, 'current', hint)
                break
    return [{'label': l, 'state': s, 'hint': h} for l, s, h in steps]


def get_response(pk):
    """A donor response with its request and donor, or None (used by the donations slice)."""
    return DonorResponse.objects.select_related('blood_request', 'donor_user').filter(pk=pk).first()


def lock_for_donation(response_pk):
    """Row-lock a response and its request inside a transaction; returns (request, response)."""
    response = DonorResponse.objects.select_for_update().get(pk=response_pk)
    item = BloodRequest.objects.select_for_update().get(pk=response.blood_request_id)
    return item, response


def mark_response_completed(response):
    response.response_status = 'completed'
    response.save(update_fields=['response_status'])


def mark_request_fulfilled(item):
    """Close a request and return its donors so they can be told."""
    item.status = 'fulfilled'
    item.save(update_fields=['status'])
    return [offer.donor_user for offer in item.donor_responses.select_related('donor_user')]
