"""Location, maps and collection-facility regressions; uses isolated test DB."""
from datetime import timedelta
from io import StringIO
from django import forms
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from apps.shared.locations import pack, unpack, coordinates, display_location, distance_km, location_matches, catalog
from apps.shared.widgets import LocationField
from apps.facilities.models import Facility
from apps.notifications.models import Notification
from apps.profile.models import Profile
from .models import BloodRequest, DonorResponse

COUNTRY='PH'
REGION='0702200000'
CITY='0730600000'
POINT=(10.3157,123.8854)
def pinned(lat=POINT[0],lng=POINT[1],address='Collection entrance',precision='pin'):
    return pack(COUNTRY,REGION,CITY,lat,lng,address,precision)
def location_post(prefix='location',**changes):
    result={f'{prefix}_{i}':value for i,value in enumerate([COUNTRY,REGION,CITY,'Collection entrance',*POINT,'pin',''])}
    result.update(changes)
    return result

class GeographicFieldTests(TestCase):
    def test_dropdown_city_fills_approximate_coordinates(self):
        value=LocationField().clean([COUNTRY,REGION,CITY,'',None,None,'legacy',''])
        self.assertEqual(unpack(value)['precision'],'city')
        self.assertIsNotNone(coordinates(value))
        self.assertIn('Cebu City',display_location(value))
    def test_country_region_city_relationship_validated(self):
        field=LocationField()
        for values in [['US',REGION,CITY,'',*POINT,'pin',''],[COUNTRY,'invalid',CITY,'',*POINT,'pin',''],[COUNTRY,REGION,'999999999','',*POINT,'pin','']]:
            with self.assertRaises(forms.ValidationError):field.clean(values)
    def test_bad_coordinates_and_partial_pair_rejected(self):
        for lat,lng in [(91,123),(10,181),(10,None),(float('nan'),123)]:
            with self.assertRaises(forms.ValidationError):LocationField().clean([COUNTRY,REGION,CITY,'',lat,lng,'pin',''])
    def test_custom_city_requires_name_and_pin(self):
        for lat,lng,custom in [(None,None,'Small town'),(*POINT,'')]:
            with self.assertRaises(forms.ValidationError):LocationField().clean([COUNTRY,'','__custom__','',lat,lng,'pin',custom])
        value=LocationField().clean([COUNTRY,'','__custom__','',*POINT,'pin','Small town'])
        self.assertIn('Small town',display_location(value))
    def test_existing_column_length_enforced(self):
        with self.assertRaises(forms.ValidationError):LocationField(max_length=150).clean([COUNTRY,REGION,CITY,'x'*150,*POINT,'pin',''])
    def test_legacy_and_malformed_tagged_values(self):
        self.assertEqual(LocationField().clean(' Cebu City '),'Cebu City')
        self.assertEqual(LocationField(required=False).clean(''),'')
        with self.assertRaises(forms.ValidationError):LocationField().clean('BS1:["bad"]')
    def test_radius_across_nearby_cities_and_legacy_fallback(self):
        other=pack('PH','0702200000','0730700000',10.31,123.92,'','pin')
        self.assertTrue(location_matches(pinned(),other,5))
        self.assertFalse(location_matches(pinned(),other,1))
        self.assertTrue(location_matches(pinned(),'Cebu City',25))
        self.assertFalse(location_matches(pinned(),'Manila',25))
        self.assertAlmostEqual(distance_km(pinned(),pinned()),0)
    def test_unchanged_legacy_profile_survives_other_edits(self):
        from apps.profile.forms import ProfileForm
        user=User.objects.create_user('legacy-location')
        profile=user.bloodseekr_profile
        for old in ['Cebu City','Old unlisted neighborhood','10.3123456,123.886789']:
            profile.location=old;profile.save()
            field=ProfileForm(instance=profile).fields['location']
            values=field.widget.decompress(old)
            data={f'location_{i}':v for i,v in enumerate(values)}
            data['phone_number']='09171234567'
            form=ProfileForm(data,instance=profile)
            self.assertTrue(form.is_valid(),form.errors)
            self.assertEqual(form.save().location,old)
    def test_catalog_api_filters_province(self):
        response=self.client.get('/locations/options/',{'country':'PH','province':REGION})
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json()['cities'])
        self.assertTrue(all(c['region']==REGION for c in response.json()['cities']))
        self.assertEqual(self.client.get('/locations/options/',{'country':'INVALID'}).status_code,400)

class CollectionMapTests(TestCase):
    def setUp(self):
        call_command('seed_blood_data',stdout=StringIO())
        self.owner=User.objects.create_user('requester','owner@example.com','Password123!')
        self.donor=User.objects.create_user('volunteer','donor@example.com','Password123!')
        self.staff=User.objects.create_user('staff','staff@example.com','Password123!',is_staff=True)
        Profile.objects.filter(user=self.donor).update(blood_type_id='O-',available_to_donate=True,phone_number='09171234567',location=pinned(address=''))
        self.facility=Facility.objects.create(name='Test collection center',facility_type='blood_center',city='Cebu City',address=pinned(),is_verified=True)
        self.item=BloodRequest.objects.create(requester=self.owner,required_blood_type_id='A+',patient_name='PRIVATE PATIENT',units_needed=2,urgency='urgent',needed_date=timezone.localdate()+timedelta(days=2),location=pinned(),facility=self.facility,status="open",verification_status="pending")
        self.client.force_login(self.owner)
    def test_map_requires_login_and_keeps_patient_identity_private(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('blood_requests:map_data')).status_code,302)
        self.client.force_login(self.staff)
        data=self.client.get(reverse('blood_requests:map_data'),{'view':'community'})
        self.assertNotContains(data,'PRIVATE PATIENT')
        self.assertNotContains(data,'owner@example.com')
        self.assertEqual(data['Cache-Control'],'private, no-store')
        self.assertEqual(data['Referrer-Policy'],'strict-origin-when-cross-origin')
        self.assertEqual(data.json()['points'][0]['url'],reverse('blood_requests:detail',args=[self.item.pk]))
    def test_ineligible_community_map_does_not_grant_detail_access(self):
        user=User.objects.create_user('viewer')
        self.client.force_login(user)
        data=self.client.get(reverse('blood_requests:map_data'),{'view':'community'}).json()
        self.assertEqual(data['points'][0]['url'],'')
        self.assertEqual(self.client.get(reverse('blood_requests:detail',args=[self.item.pk])).status_code,403)
        response=self.client.get(reverse('blood_requests:list'),{'view':'community'})
        self.assertNotContains(response,'PRIVATE PATIENT')
        self.assertNotContains(self.client.get(reverse('facilities:detail',args=[self.facility.pk])),'PRIVATE PATIENT')
    def test_matching_filters_radius_and_map_preferences(self):
        self.client.force_login(self.donor)
        data=self.client.get(reverse('blood_requests:map_data')).json()
        self.assertEqual(data['total'],1)
        self.assertEqual(data['my_location'],list(POINT))
        self.assertEqual(data['radius_km'],25)
        self.item.location=pinned(lat=14.6,lng=120.98);self.item.save()
        self.assertEqual(self.client.get(reverse('blood_requests:map_data')).json()['total'],0)
    def test_unpinned_count_and_filters(self):
        self.item.location='Cebu City';self.item.save()
        data=self.client.get(reverse('blood_requests:map_data'),{'view':'mine'}).json()
        self.assertEqual(data['unmapped_count'],1);self.assertEqual(data['points'],[])
        self.assertEqual(self.client.get(reverse('blood_requests:map_data'),{'view':'mine','urgency':'routine'}).json()['total'],0)
    def test_facility_prefills_request_and_options_are_readable(self):
        response=self.client.get(reverse('blood_requests:create'),{'facility':self.facility.pk})
        self.assertEqual(response.context['form'].initial['location'],self.facility.address)
        data=self.client.get(reverse('facilities:options')).json()['facilities'][0]
        self.assertEqual(data['city'],'Cebu City');self.assertEqual(data['lat'],POINT[0])
        self.assertNotIn('BS1:',data['address'])
        self.assertContains(self.client.get(reverse('facilities:detail',args=[self.facility.pk])),'Create request here')
    def test_only_staff_can_manage_facilities(self):
        self.assertEqual(self.client.get(reverse('facilities:add')).status_code,403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('facilities:add')).status_code,200)
        result=self.client.post(reverse('facilities:add'),{'name':'New center','facility_type':'clinic','contact_email':'desk@example.com','contact_phone':'0917',**location_post('address')})
        self.assertEqual(result.status_code,302)
        facility=Facility.objects.get(name='New center')
        self.assertEqual(facility.city,'Cebu City');self.assertFalse(facility.is_verified)
    def test_owner_can_update_point_and_notify_existing_donor(self):
        DonorResponse.objects.create(blood_request=self.item,donor_user=self.donor,response_status="pending")
        data=location_post(location_3='New entrance',location_4='10.32')
        result=self.client.post(reverse('blood_requests:edit_location',args=[self.item.pk]),dict(data,facility=self.facility.pk))
        self.assertEqual(result.status_code,302)
        self.item.refresh_from_db();self.assertEqual(coordinates(self.item.location)[0],10.32)
        self.assertTrue(Notification.objects.filter(user=self.donor,notification_type='collection_update').exists())
        self.client.force_login(self.donor)
        self.assertEqual(self.client.post(reverse('blood_requests:edit_location',args=[self.item.pk]),data).status_code,404)
    def test_facility_contact_edit_preserves_legacy_address_and_city(self):
        from apps.facilities.forms import FacilityForm
        self.facility.address='Old street entrance';self.facility.save()
        field=FacilityForm(instance=self.facility).fields['address']
        data={f'address_{i}':v for i,v in enumerate(field.widget.decompress(self.facility.address))}
        form=FacilityForm(dict(data,name=self.facility.name,facility_type='blood_center',contact_phone='0917',contact_email='updated@example.com'),instance=self.facility)
        self.assertTrue(form.is_valid(),form.errors)
        item=form.save()
        self.assertEqual(item.address,'Old street entrance');self.assertEqual(item.city,'Cebu City')
    def test_closed_request_location_cannot_change(self):
        self.item.status='fulfilled';self.item.save()
        self.assertEqual(self.client.post(reverse('blood_requests:edit_location',args=[self.item.pk]),location_post()).status_code,403)
    @override_settings(GOOGLE_MAPS_BROWSER_KEY='test-public-key',GOOGLE_MAPS_MAP_ID='test-map-id')
    def test_optional_browser_key_rendered_in_map_configuration(self):
        response=self.client.get(reverse('blood_requests:list'))
        self.assertContains(response,'test-public-key');self.assertContains(response,'test-map-id')
