from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification


def _group_label(created, today):
    days = (today - timezone.localtime(created).date()).days
    return 'Today' if days <= 0 else 'Yesterday' if days == 1 else 'This week' if days < 7 else 'Earlier'


@login_required
def notification_list(request):
    unread_only = request.GET.get('unread') == '1'
    base = Notification.objects.filter(user=request.user)
    notices = base.select_related('blood_request').order_by('-created_at')
    if unread_only:
        notices = notices.filter(is_read=False)
    page_obj = Paginator(notices, 20).get_page(request.GET.get('page'))
    today = timezone.localdate()
    for notice in page_obj:
        notice.group = _group_label(notice.created_at, today)
    return render(request, 'notifications/list.html', {
        'page_obj': page_obj, 'unread_only': unread_only,
        'unread_total': base.filter(is_read=False).count(), 'total': base.count(),
    })


@login_required
@require_POST
def mark_read(request, pk):
    notice = get_object_or_404(Notification, pk=pk, user=request.user)
    notice.is_read = True
    notice.save(update_fields=['is_read'])
    # "Open" buttons mark as read and continue to the related request.
    if request.POST.get('open') and notice.blood_request_id:
        return redirect('blood_requests:detail', pk=notice.blood_request_id)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, f'Marked {updated} notification{"s" if updated != 1 else ""} as read.' if updated else 'You are all caught up.')
    return redirect('notifications:list')
