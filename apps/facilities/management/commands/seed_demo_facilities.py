from django.core.management.base import BaseCommand
from apps.facilities.models import Facility
from apps.shared.locations import pack,coordinates
class Command(BaseCommand):
    help='Add clearly labelled fictional Cebu demo facilities with map points. Existing real facilities are unchanged.'
    def handle(self,*args,**options):
        for name,kind,lat,lng in [('BloodSeekr Demo Blood Center','blood_center',10.3157,123.8854),('BloodSeekr Demo Hospital','hospital',10.3210,123.9120)]:
            address=pack('PH','0702200000','0730600000',lat,lng,'Fictional demo collection point','pin')
            item,created=Facility.objects.get_or_create(name=name,city='Cebu City',defaults={'facility_type':kind,'address':address,'contact_phone':'Not provided','contact_email':'demo@example.com','is_verified':False})
            if not created and not coordinates(item.address) and item.address.startswith('Demo address'):
                item.address=address;item.save(update_fields=['address'])
        self.stdout.write(self.style.SUCCESS('Fictional demo facilities ready. These are not real hospital locations.'))
