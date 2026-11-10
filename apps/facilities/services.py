from django.urls import reverse
from apps.shared.locations import coordinates,display_location,city_name,directions_url
from .models import Facility

def facility_option(item):
    point=coordinates(item.address)
    return {'id':item.pk,'name':item.name,'type':item.facility_type,'city':item.city,'address':display_location(item.address),'location_value':item.address if point else item.city,'lat':point[0] if point else None,'lng':point[1] if point else None,'verified':item.is_verified,'phone':item.contact_phone,'detail_url':reverse('facilities:detail',args=[item.pk]),'directions_url':directions_url(item.address if point else item.address+', '+item.city)}


def facility_options():
    """Picker options for the request forms (verified first)."""
    return [facility_option(x) for x in Facility.objects.order_by('-is_verified', 'name')]


def get_facility(pk):
    return Facility.objects.filter(pk=pk).first() if str(pk or '').isdigit() else None
