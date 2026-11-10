from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from apps.shared.locations import coordinates,display_location,distance_km,unpack
from apps.facilities.services import facility_option, facility_options, get_facility
from apps.blood_data.services import ACTIVE_STATUSES, donor_eligible, blood_types, matching_requests, matching_donors
from apps.notifications.services import notify, notify_matches
from .models import BloodRequest, DonorResponse
from .forms import BloodRequestForm, DonorResponseForm, RequestStatusForm
from .services import can_view, attach_progress, timeline, pending_offers_for

def get_visible(request, pk):
    item = get_object_or_404(BloodRequest.objects.select_related('facility','required_blood_type','requester'), pk=pk)
    if not can_view(request.user, item):
        raise PermissionDenied('This request is available to its owner and eligible donors.')
    return item

def visible_items(request):
    mode=request.GET.get('view','matching')
    qs=BloodRequest.objects.select_related('required_blood_type','facility').order_by('needed_date','-created_at')
    if mode=='mine':items=list(qs.filter(requester=request.user))
    elif mode=='responses':items=list(qs.filter(donor_responses__donor_user=request.user))
    elif mode=='community':items=list(qs.filter(status__in=ACTIVE_STATUSES,needed_date__gte=timezone.localdate()).exclude(verification_status='rejected'))
    else:mode='matching';items=matching_requests(request.user)
    urgency=request.GET.get('urgency','')
    blood=request.GET.get('blood','')
    query=request.GET.get('q','').strip().casefold()
    profile=getattr(request.user,'bloodseekr_profile',None)
    filtered=[]
    for item in items:
        if urgency in ('routine','urgent','emergency') and item.urgency!=urgency:continue
        if blood and item.required_blood_type_id!=blood:continue
        if query and query not in display_location(item.location).casefold() and query not in str(item.facility or '').casefold():continue
        item.can_open=can_view(request.user,item)
        item.distance=distance_km(profile.location,item.location) if profile else None
        filtered.append(item)
    if request.GET.get('sort')=='nearby':filtered.sort(key=lambda x:x.distance if x.distance is not None else float('inf'))
    return mode,filtered

TABS = [('community', 'Community'), ('matching', 'My matches'), ('mine', 'My requests'), ('responses', 'My responses')]


@login_required
def request_list(request):
    mode, items = visible_items(request)
    page_obj = Paginator(items, 12).get_page(request.GET.get('page'))
    attach_progress(page_obj.object_list)
    filters = {key: request.GET.get(key, '') for key in ('q', 'blood', 'urgency', 'sort')}
    return render(request, 'blood_requests/list.html', {
        'page_obj': page_obj, 'mode': mode, 'tabs': TABS, 'urgency': filters['urgency'], 'blood': filters['blood'],
        'query': filters['q'], 'sort': filters['sort'], 'blood_types': blood_types(), 'result_count': len(items),
        'has_filters': any(filters.values()), 'pending_offer_count': pending_offers_for(request.user).count(),
    })

@login_required
@require_GET
def request_map_data(request):
    mode,items=visible_items(request)
    points=[];unpinned=0
    for item in items:
        point=coordinates(item.location)
        if not point:unpinned+=1;continue
        points.append({'id':item.pk,'lat':point[0],'lng':point[1],'title':f'{item.required_blood_type_id} · Request #{item.pk}','subtitle':display_location(item.location),'blood_type':item.required_blood_type_id,'urgency':item.urgency,'status':item.status,'units':item.units_needed,'facility':str(item.facility or ''),'needed_date':str(item.needed_date),'distance_km':round(item.distance,1) if item.distance is not None else None,'approximate':unpack(item.location)['precision']=='city','url':reverse('blood_requests:detail',args=[item.pk]) if item.can_open else ''})
    profile=getattr(request.user,'bloodseekr_profile',None)
    preferences=getattr(request.user,'bloodseekr_settings',None)
    response=JsonResponse({'points':points,'unmapped_count':unpinned,'total':len(items),'mode':mode,'my_location':coordinates(profile.location) if profile else None,'radius_km':preferences.match_radius_km if preferences else 25})
    response['Cache-Control']='private, no-store'
    return response

@login_required
def create_request(request):
    initial={}
    selected_facility=get_facility(request.GET.get("facility"))
    if selected_facility:
        initial={"facility":selected_facility,"location":selected_facility.address if coordinates(selected_facility.address) else selected_facility.city}
    form = BloodRequestForm(request.POST or None,initial=initial)
    if request.method == 'POST':
        valid = form.is_valid()
        if valid:
            with transaction.atomic():
                item = form.save(commit=False)
                item.requester = request.user
                item.status = 'open'
                item.verification_status = 'verified'
                item.save()
                notify_matches(item)
            messages.success(request,'Blood request posted. Matching donors have been notified.')
            return redirect('blood_requests:detail',pk=item.pk)
    return render(request,'blood_requests/form.html',{'form':form,'facility_options':facility_options()})

@login_required
def request_detail(request, pk):
    item = get_visible(request, pk)
    attach_progress([item])
    owner = item.requester_id == request.user.pk
    response = item.donor_responses.filter(donor_user=request.user).first()
    all_responses = list(item.donor_responses.select_related('donor_user', 'donor_user__bloodseekr_profile', 'donation_record').order_by('-responded_at'))
    point = coordinates(item.location)
    return render(request, 'blood_requests/detail.html', {
        'item': item, 'owner': owner,
        'can_respond': not response and donor_eligible(request.user, item),
        'my_response': response,
        'responses': all_responses if owner or request.user.is_staff else [],
        'response_form': DonorResponseForm(),
        'matched_donors': matching_donors(item, visible_only=True) if owner else [],
        'active': item.status in ACTIVE_STATUSES,
        'steps': timeline(item, all_responses),
        'map_points': [{'lat': point[0], 'lng': point[1], 'title': f'{item.required_blood_type_id} · Request #{item.pk}', 'subtitle': display_location(item.location), 'url': ''}] if point else [],
    })


@login_required
@require_POST
def respond(request, pk):
    form = DonorResponseForm(request.POST)
    with transaction.atomic():
        item = get_object_or_404(BloodRequest.objects.select_for_update(),pk=pk)
        if not donor_eligible(request.user,item):
            raise PermissionDenied('Your donor profile does not currently match this request.')
        if form.is_valid():
            response,created = DonorResponse.objects.get_or_create(blood_request=item,donor_user=request.user,defaults={'response_status':'pending','notes':form.cleaned_data['notes']})
            if created:
                notify(item.requester,item,'donor_response','A donor responded',f'{request.user.get_full_name() or request.user.username} offered to help with request #{pk}.')
                messages.success(request,'Your offer has been sent to the requester.')
            else:
                messages.info(request,'You already responded to this request.')
        else:
            messages.error(request,'Please keep notes within 2,000 characters.')
    return redirect('blood_requests:detail',pk=pk)

@login_required
@require_POST
def response_action(request, pk, response_pk):
    action = request.POST.get('action')
    with transaction.atomic():
        item = get_object_or_404(BloodRequest.objects.select_for_update(),pk=pk)
        response = get_object_or_404(DonorResponse.objects.select_for_update(),pk=response_pk,blood_request=item)
        if action == 'withdraw' and response.donor_user_id == request.user.pk:
            if response.response_status not in ('pending','accepted') or hasattr(response,'donation_record'):
                messages.error(request,'This offer can no longer be withdrawn.')
                return redirect('blood_requests:detail',pk=pk)
            response.response_status = 'withdrawn'
            recipient = item.requester
        elif item.requester_id == request.user.pk and action in ('accept','decline'):
            if item.status not in ACTIVE_STATUSES or response.response_status != 'pending':
                messages.error(request,'This offer can no longer be changed.')
                return redirect('blood_requests:detail',pk=pk)
            if action == 'accept' and not donor_eligible(response.donor_user,item):
                messages.error(request,'The donor no longer matches this request.')
                return redirect('blood_requests:detail',pk=pk)
            response.response_status = 'accepted' if action == 'accept' else 'declined'
            recipient = response.donor_user
            if action == 'accept':
                item.status = 'in_progress'
                item.save(update_fields=['status'])
        else:
            raise PermissionDenied
        response.save(update_fields=['response_status'])
        notify(recipient,item,'response_update','Donor response updated',f'Response for request #{pk}: {response.response_status}.')
        messages.success(request,'Donor response updated.')
    return redirect('blood_requests:detail',pk=pk)

@login_required
@require_POST
def update_status(request, pk):
    form = RequestStatusForm(request.POST)
    with transaction.atomic():
        item = get_object_or_404(BloodRequest.objects.select_for_update(),pk=pk,requester=request.user)
        if form.is_valid():
            status = form.cleaned_data['status']
            if item.status in ('fulfilled','cancelled') and status != item.status:
                messages.error(request,'Closed requests cannot be reopened. Create a new request if needed.')
            elif status != item.status:
                item.status = status
                item.save(update_fields=['status'])
                for response in item.donor_responses.select_related('donor_user'):
                    notify(response.donor_user,item,'request_status','Blood request updated',f'Request #{pk} is now {status}.')
                messages.success(request,'Request status updated.')
        else:
            messages.error(request,'Choose a valid request status.')
    return redirect('blood_requests:detail',pk=pk)

@login_required
def edit_location(request,pk):
    from .forms import RequestLocationForm
    item=get_object_or_404(BloodRequest,pk=pk,requester=request.user)
    if item.status not in ACTIVE_STATUSES:
        raise PermissionDenied('Closed request locations cannot be changed.')
    form=RequestLocationForm(request.POST or None,instance=item)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            locked=BloodRequest.objects.select_for_update().get(pk=pk)
            if locked.status not in ACTIVE_STATUSES:raise PermissionDenied
            locked.location=form.cleaned_data['location']
            locked.facility=form.cleaned_data['facility']
            locked.save(update_fields=['location','facility'])
            for response in locked.donor_responses.select_related('donor_user'):
                notify(response.donor_user,locked,'collection_update','Collection location updated',f'The collection location for request #{pk} has changed. Review it before attending.')
        messages.success(request,'Collection location updated.')
        return redirect('blood_requests:detail',pk=pk)
    return render(request,'blood_requests/location_form.html',{'form':form,'item':item,'facility_options':facility_options()})
