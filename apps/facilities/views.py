from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q,Count
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from django.views.decorators.http import require_GET
from apps.shared.locations import coordinates,distance_km,directions_url
from apps.blood_data.services import ACTIVE_STATUSES
from .models import Facility
from .forms import FacilityForm
from .services import facility_option
from apps.blood_requests.services import can_view, attach_progress
@login_required
def facility_list(request):
    query=request.GET.get('q','').strip()
    kind=request.GET.get('type','')
    verified=request.GET.get('verified')=='1'
    qs=Facility.objects.annotate(active_request_count=Count('blood_requests',filter=Q(blood_requests__status__in=ACTIVE_STATUSES,blood_requests__needed_date__gte=timezone.localdate()) & ~Q(blood_requests__verification_status='rejected'))).order_by('city','name')
    if query:qs=qs.filter(Q(name__icontains=query)|Q(city__icontains=query))
    if kind in ('hospital','blood_center','clinic'):qs=qs.filter(facility_type=kind)
    if verified:qs=qs.filter(is_verified=True)
    facilities=list(qs)
    profile=getattr(request.user,'bloodseekr_profile',None)
    for item in facilities:
        item.distance=distance_km(profile.location,item.address) if profile else None
        item.directions=directions_url(item.address)
    if request.GET.get('sort')=='nearby':facilities.sort(key=lambda f:f.distance if f.distance is not None else float('inf'))
    return render(request,'facilities/list.html',{'page_obj':Paginator(facilities,12).get_page(request.GET.get('page')),'query':query,'kind':kind,'verified_only':verified,'sort':request.GET.get('sort',''),'facility_count':len(facilities)})
@login_required
def facility_detail(request,pk):
    facility=get_object_or_404(Facility,pk=pk)
    items=facility.blood_requests.filter(status__in=ACTIVE_STATUSES,needed_date__gte=timezone.localdate()).exclude(verification_status='rejected').select_related('required_blood_type','facility').order_by('needed_date')
    items=attach_progress(items)
    for item in items:item.can_open=can_view(request.user,item)
    completed=facility.donation_records.filter(donation_status='completed').count()
    data=facility_option(facility)
    return render(request,'facilities/detail.html',{'facility':facility,'mode':'community','active_requests':items,'completed_count':completed,'facility_data':data,'map_points':[{'lat':data['lat'],'lng':data['lng'],'title':facility.name,'subtitle':data['address'],'url':'','type':'facility'}] if data['lat'] is not None else []})
@login_required
def manage_facility(request,pk=None):
    if not request.user.is_staff:raise PermissionDenied
    item=get_object_or_404(Facility,pk=pk) if pk else None
    form=FacilityForm(request.POST or None,instance=item)
    if request.method=='POST' and form.is_valid():
        facility=form.save()
        messages.success(request,'Facility saved. Verification is managed by staff in admin.')
        return redirect('facilities:detail',pk=facility.pk)
    return render(request,'facilities/form.html',{'form':form,'facility':item})
@login_required
@require_GET
def facility_options(request):
    return JsonResponse({'facilities':[facility_option(x) for x in Facility.objects.order_by('-is_verified','city','name')]})
