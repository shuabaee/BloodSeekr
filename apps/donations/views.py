import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, HttpResponse
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404,redirect,render
from apps.blood_requests import services as requests_api
from apps.notifications.services import notify
from .models import DonationRecord
from .forms import DonationForm
from . import services
ROLES = {'all': 'All records', 'donor': 'My donations', 'requester': 'For my requests'}


@login_required
def donation_list(request):
    role = request.GET.get('role', 'all')
    role = role if role in ROLES else 'all'
    qs = services.records_for(request.user, role)
    return render(request, 'donations/list.html', {
        'page_obj': Paginator(qs, 15).get_page(request.GET.get('page')),
        'role': role, 'roles': ROLES, 'summary': services.summary_for(request.user), 'total': qs.count(),
    })


@login_required
def export_csv(request):
    """Download the records shown in the list as a spreadsheet-friendly CSV file."""
    role = request.GET.get('role', 'all')
    role = role if role in ROLES else 'all'
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="bloodseekr-donations.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Request #', 'Donor', 'Facility', 'Units', 'Screening', 'Status'])
    for r in services.records_for(request.user, role):
        donor = r.donor_response.donor_user
        writer.writerow([r.donation_date, r.donor_response.blood_request_id, donor.get_full_name() or donor.username, r.facility, r.units_donated, r.screening_status, r.donation_status])
    return response
@login_required
def record_donation(request,response_pk):
    response = requests_api.get_response(response_pk)
    if response is None:
        raise Http404('Donor response not found.')
    if not (request.user.is_staff or response.blood_request.requester_id == request.user.pk):
        raise PermissionDenied('Only the requester or staff can record a coordinated donation.')
    record = DonationRecord.objects.filter(donor_response=response).first()
    form = DonationForm(request.POST or None,instance=record,initial={'facility':response.blood_request.facility_id,'screening_status':'pending','donation_status':'scheduled','units_donated':0})
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item, locked = requests_api.lock_for_donation(response.pk)
            existing = DonationRecord.objects.filter(donor_response=locked).first()
            if locked.response_status not in ('accepted','completed'):
                messages.error(request,'Accept the donor response before recording a donation.')
                return redirect('blood_requests:detail',pk=item.pk)
            if existing and (existing.donation_status == 'completed' or not record):
                messages.info(request,'A donation record already exists; completed records are read-only.')
                return redirect('donations:list')
            if item.verification_status == 'rejected' or item.status == 'cancelled' or (item.status == 'fulfilled' and not existing):
                messages.error(request,'This request is closed.')
                return redirect('blood_requests:detail',pk=item.pk)
            record = form.save(commit=False)
            record.donor_response = locked
            record.save()
            if record.donation_status == 'completed':
                requests_api.mark_response_completed(locked)
                total = DonationRecord.objects.filter(donor_response__blood_request=item,donation_status='completed',screening_status='passed').aggregate(total=Sum('units_donated'))['total'] or 0
                if total >= item.units_needed and item.status != 'fulfilled':
                    for donor in requests_api.mark_request_fulfilled(item):
                        notify(donor,item,'request_status','Blood request fulfilled',f'Request #{item.pk} has reached its requested units.')
            notify(locked.donor_user,item,'donation_record','Donation record updated',f'Your donation for request #{item.pk} is {record.donation_status}.')
            messages.success(request,'Donation record saved.')
        return redirect('donations:list')
    if response.response_status not in ('accepted','completed'):
        messages.error(request,'Accept the donor response first.')
        return redirect('blood_requests:detail',pk=response.blood_request_id)
    if record and record.donation_status == 'completed':
        messages.info(request,'Completed donation records are read-only.')
        return redirect('donations:list')
    return render(request,'donations/form.html',{'form':form,'response':response})
