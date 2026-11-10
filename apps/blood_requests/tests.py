from datetime import timedelta
from decimal import Decimal
from io import StringIO
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.blood_data.models import BloodCompatibility
from apps.blood_data.services import matching_requests, donor_eligible, location_matches
from apps.profile.models import Profile
from apps.facilities.models import Facility
from apps.notifications.models import Notification
from apps.donations.models import DonationRecord
from .models import BloodRequest, DonorResponse, RequestAttachment

class BloodSeekrWorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_blood_data',stdout=StringIO())
        self.owner = User.objects.create_user('owner','owner@example.com','SafePassword123!',first_name='Requester')
        self.donor = User.objects.create_user('donor','donor@example.com','SafePassword123!',first_name='Volunteer')
        self.other = User.objects.create_user('other','other@example.com','SafePassword123!')
        self.staff = User.objects.create_user('reviewer','staff@example.com','SafePassword123!',is_staff=True,is_superuser=True)
        Profile.objects.filter(user=self.donor).update(blood_type_id='O-',available_to_donate=True,location='Cebu City',phone_number='09171234567')
        self.facility = Facility.objects.create(name='Test hospital',facility_type='hospital',address='Test address',city='Cebu City',contact_phone='000',contact_email='hospital@example.com')
        self.payload = {'required_blood_type':'A+','patient_name':'Test Patient','units_needed':1,'urgency':'urgent','needed_date':str(timezone.localdate()+timedelta(days=1)),'location':'Cebu City','facility':self.facility.pk}
        self.client.force_login(self.owner)
    def create_request(self,**changes):
        payload = dict(self.payload,**changes)
        response = self.client.post(reverse('blood_requests:create'),payload)
        self.assertEqual(response.status_code,302)
        return BloodRequest.objects.latest('pk')
    def offer(self,item):
        self.client.force_login(self.donor)
        return self.client.post(reverse('blood_requests:respond',args=[item.pk]),{'notes':'Available today'})
    def accept(self,item):
        self.offer(item)
        offer = DonorResponse.objects.get(blood_request=item,donor_user=self.donor)
        self.client.force_login(self.owner)
        response = self.client.post(reverse('blood_requests:response_action',args=[item.pk,offer.pk]),{'action':'accept'})
        self.assertEqual(response.status_code,302)
        return offer
    def donation_data(self,**changes):
        return dict({'facility':self.facility.pk,'donation_date':str(timezone.localdate()),'units_donated':'1.00','screening_status':'passed','donation_status':'completed'},**changes)
    def test_request_creation_matching_and_notifications(self):
        item = self.create_request()
        self.assertEqual(item.requester,self.owner)
        self.assertEqual(item.verification_status,'verified')
        self.assertEqual(item.status,'open')
        self.assertIn(item,matching_requests(self.donor))
        self.assertFalse(donor_eligible(self.owner,item))
        self.assertTrue(Notification.objects.filter(user=self.donor,blood_request=item,notification_type='matching_request').exists())
    def test_invalid_requests_do_not_save(self):
        for changes in [{'units_needed':0},{'needed_date':str(timezone.localdate()-timedelta(days=1))},{'urgency':'made-up'},{'patient_name':''}]:
            response=self.client.post(reverse('blood_requests:create'),dict(self.payload,**changes))
            self.assertEqual(response.status_code,200)
        self.assertEqual(BloodRequest.objects.count(),0)
    def test_owner_and_eligible_donor_can_view(self):
        item=self.create_request()
        self.assertEqual(self.client.get(reverse('blood_requests:detail',args=[item.pk])).status_code,200)
        self.client.force_login(self.donor)
        self.assertEqual(self.client.get(reverse('blood_requests:detail',args=[item.pk])).status_code,200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('blood_requests:detail',args=[item.pk])).status_code,403)
    def test_duplicate_response_prevented(self):
        item=self.create_request()
        self.offer(item);self.offer(item)
        self.assertEqual(DonorResponse.objects.filter(blood_request=item,donor_user=self.donor).count(),1)
        self.assertEqual(Notification.objects.filter(user=self.owner,notification_type='donor_response').count(),1)
        with self.assertRaises(IntegrityError),transaction.atomic():
            DonorResponse.objects.create(blood_request=item,donor_user=self.donor,response_status='pending')
    def test_matching_checks_compatibility_availability_location_and_expiry(self):
        item=self.create_request()
        for field,value in [('blood_type_id','B+'),('available_to_donate',False),('location','Manila')]:
            old=getattr(self.donor.bloodseekr_profile,field)
            Profile.objects.filter(user=self.donor).update(**{field:value})
            self.assertFalse(donor_eligible(self.donor,item))
            Profile.objects.filter(user=self.donor).update(**{field:old})
        item.status='cancelled';item.save()
        self.assertFalse(donor_eligible(self.donor,item))
        item.status='open';item.needed_date=timezone.localdate()-timedelta(days=1);item.save()
        self.assertFalse(donor_eligible(self.donor,item))
    def test_compatibility_direction_and_explicit_false(self):
        item=self.create_request(required_blood_type='O-')
        Profile.objects.filter(user=self.donor).update(blood_type_id='A+')
        self.assertFalse(donor_eligible(self.donor,item))
        Profile.objects.filter(user=self.donor).update(blood_type_id='O-')
        BloodCompatibility.objects.filter(donor_blood_type_id='O-',recipient_blood_type_id='O-').update(is_compatible=False)
        self.assertFalse(donor_eligible(self.donor,item))
    def test_radius_and_text_locality(self):
        self.assertTrue(location_matches('10.3000,123.9000','10.3010,123.9010',1))
        self.assertFalse(location_matches('10.3000,123.9000','14.6000,120.9800',25))
        self.assertTrue(location_matches(' Cebu City ','cebu city',25))
        self.assertFalse(location_matches('Cebu','Cebu City',25))
        self.assertFalse(location_matches('','',25))
    def test_profile_privacy_hides_discovery_but_allows_self_response(self):
        self.donor.bloodseekr_settings.show_donor_profile=False
        self.donor.bloodseekr_settings.save()
        item=self.create_request()
        response=self.client.get(reverse('blood_requests:detail',args=[item.pk]))
        self.assertEqual(response.context['matched_donors'],[])
        self.assertTrue(donor_eligible(self.donor,item))
        self.assertEqual(self.offer(item).status_code,302)
    def test_emergency_notification_preference(self):
        prefs=self.donor.bloodseekr_settings;prefs.emergency_notifications=False;prefs.save()
        item=self.create_request(urgency='emergency')
        self.assertFalse(Notification.objects.filter(user=self.donor,blood_request=item).exists())
        self.assertTrue(donor_eligible(self.donor,item))
    def test_ineligible_or_requester_cannot_respond(self):
        item=self.create_request()
        self.assertEqual(self.client.post(reverse('blood_requests:respond',args=[item.pk])).status_code,403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('blood_requests:respond',args=[item.pk])).status_code,403)
        self.assertEqual(DonorResponse.objects.count(),0)
    def test_owner_accepts_and_records_donation_end_to_end(self):
        item=self.create_request();offer=self.accept(item)
        item.refresh_from_db();offer.refresh_from_db()
        self.assertEqual(item.status,'in_progress');self.assertEqual(offer.response_status,'accepted')
        response=self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.assertEqual(response.status_code,302)
        donation=DonationRecord.objects.get(donor_response=offer)
        self.assertEqual(donation.units_donated,Decimal('1.00'))
        self.assertEqual(donation.facility,self.facility)
        item.refresh_from_db();offer.refresh_from_db()
        self.assertEqual(item.status,'fulfilled');self.assertEqual(offer.response_status,'completed')
        self.assertTrue(Notification.objects.filter(user=self.donor,notification_type='donation_record').exists())
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.assertEqual(DonationRecord.objects.filter(donor_response=offer).count(),1)
        self.client.force_login(self.donor)
        self.assertContains(self.client.get(reverse('donations:list')),'1.00')
    def test_donation_requires_acceptance_and_authorized_recorder(self):
        item=self.create_request();self.offer(item)
        offer=DonorResponse.objects.get(blood_request=item)
        self.assertEqual(self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data()).status_code,403)
        self.client.force_login(self.owner)
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.assertEqual(DonationRecord.objects.count(),0)
    def test_completed_donation_validation(self):
        item=self.create_request();offer=self.accept(item)
        for changes in [{'units_donated':'0'},{'screening_status':'failed'},{'donation_date':str(timezone.localdate()+timedelta(days=1))}]:
            self.assertEqual(self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data(**changes)).status_code,200)
        self.assertEqual(DonationRecord.objects.count(),0)
    def test_scheduled_donation_can_be_completed_without_duplicate(self):
        item=self.create_request(units_needed=2);offer=self.accept(item)
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data(donation_status='scheduled',screening_status='pending',units_donated='0'))
        self.assertEqual(DonationRecord.objects.count(),1)
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.assertEqual(DonationRecord.objects.count(),1)
        item.refresh_from_db();self.assertEqual(item.status,'in_progress')
    def test_one_to_one_donation_constraint(self):
        item=self.create_request();offer=self.accept(item)
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        with self.assertRaises(IntegrityError),transaction.atomic():
            DonationRecord.objects.create(donor_response=offer,facility=self.facility,donation_date=timezone.localdate(),units_donated=1,screening_status='passed',donation_status='completed')
    def test_other_user_cannot_accept_or_change_status(self):
        item=self.create_request();self.offer(item);offer=DonorResponse.objects.get(blood_request=item)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('blood_requests:response_action',args=[item.pk,offer.pk]),{'action':'accept'}).status_code,403)
        self.assertEqual(self.client.post(reverse('blood_requests:status',args=[item.pk]),{'status':'cancelled'}).status_code,404)
    def test_decline_withdraw_and_closed_request(self):
        item=self.create_request();self.offer(item);offer=DonorResponse.objects.get(blood_request=item)
        self.client.post(reverse('blood_requests:response_action',args=[item.pk,offer.pk]),{'action':'withdraw'})
        offer.refresh_from_db();self.assertEqual(offer.response_status,'withdrawn')
        self.client.force_login(self.owner)
        self.client.post(reverse('blood_requests:status',args=[item.pk]),{'status':'cancelled'})
        self.client.post(reverse('blood_requests:status',args=[item.pk]),{'status':'open'})
        item.refresh_from_db();self.assertEqual(item.status,'cancelled')
        self.assertTrue(Notification.objects.filter(user=self.donor,notification_type='request_status').exists())
    def test_document_upload_is_removed(self):
        self.assertEqual(self.client.get(reverse('blood_requests:create')).status_code,200)
        self.assertNotContains(self.client.get(reverse('blood_requests:create')),'Supporting document')
        item=self.create_request()
        self.assertNotContains(self.client.get(reverse('blood_requests:detail',args=[item.pk])),'Upload document')
    def test_mark_notifications_read_only_own(self):
        item=self.create_request();notice=Notification.objects.get(user=self.donor,blood_request=item)
        self.assertEqual(self.client.post(reverse('notifications:read',args=[notice.pk])).status_code,404)
        self.client.force_login(self.donor)
        self.client.post(reverse('notifications:read',args=[notice.pk]))
        notice.refresh_from_db();self.assertTrue(notice.is_read)
        self.assertEqual(self.client.get(reverse('notifications:read',args=[notice.pk])).status_code,405)
    def test_all_authenticated_pages_render(self):
        item=self.create_request()
        for url in ['home:home','blood_requests:list','blood_requests:create','notifications:list','donations:list','facilities:list','profile:profile','user_settings:settings']:
            self.assertEqual(self.client.get(reverse(url)).status_code,200,url)
        self.assertEqual(self.client.get(reverse('facilities:detail',args=[self.facility.pk])).status_code,200)
        self.client.force_login(self.staff)
        for url in ['/admin/blood_requests/bloodrequest/','/admin/donations/donationrecord/','/admin/profiles/profile/','/admin/facilities/facility/']:
            self.assertEqual(self.client.get(url).status_code,200,url)
    def test_new_requests_need_no_review_and_timeline_has_no_verification(self):
        item=self.create_request()
        self.assertEqual(item.verification_status,'verified')
        page=self.client.get(reverse('blood_requests:detail',args=[item.pk]))
        self.assertNotContains(page,'Awaiting verification')
    def test_authentication_and_csrf_protection(self):
        self.client.logout()
        for url in ['home:home','blood_requests:list','blood_requests:create','notifications:list','donations:list','facilities:list','profile:profile','user_settings:settings']:
            self.assertEqual(self.client.get(reverse(url)).status_code,302,url)
        csrf_client=Client(enforce_csrf_checks=True);csrf_client.force_login(self.owner)
        self.assertEqual(csrf_client.post(reverse('blood_requests:create'),self.payload).status_code,403)
    def test_seed_is_idempotent_and_preserves_existing_pair(self):
        BloodCompatibility.objects.filter(donor_blood_type_id='O-',recipient_blood_type_id='A+').update(is_compatible=False)
        call_command('seed_blood_data',stdout=StringIO())
        self.assertEqual(BloodCompatibility.objects.count(),64)
        self.assertFalse(BloodCompatibility.objects.get(donor_blood_type_id='O-',recipient_blood_type_id='A+').is_compatible)

    def test_rejected_request_cannot_accept_offer_or_record_donation(self):
        item=self.create_request();offer=self.accept(item)
        item.verification_status='rejected';item.save()
        response=self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.assertEqual(response.status_code,302)
        self.assertEqual(DonationRecord.objects.count(),0)

    def test_completed_donation_prevents_withdrawal(self):
        item=self.create_request();offer=self.accept(item)
        self.client.post(reverse('donations:record',args=[offer.pk]),self.donation_data())
        self.client.force_login(self.donor)
        self.client.post(reverse('blood_requests:response_action',args=[item.pk,offer.pk]),{'action':'withdraw'})
        offer.refresh_from_db();self.assertEqual(offer.response_status,'completed')

    def test_declined_response_remains_unique(self):
        item=self.create_request();self.offer(item)
        offer=DonorResponse.objects.get(blood_request=item)
        self.client.force_login(self.owner)
        self.client.post(reverse('blood_requests:response_action',args=[item.pk,offer.pk]),{'action':'decline'})
        offer.refresh_from_db();self.assertEqual(offer.response_status,'declined')
        self.offer(item)
        self.assertEqual(DonorResponse.objects.filter(blood_request=item).count(),1)

    def test_scheduled_donation_form_renders(self):
        item=self.create_request();offer=self.accept(item)
        response=self.client.get(reverse('donations:record',args=[offer.pk]))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Record donation')

    def test_bulk_read_only_updates_current_users_notifications(self):
        item=self.create_request();self.offer(item)
        self.client.post(reverse('notifications:read_all'))
        self.assertFalse(Notification.objects.filter(user=self.donor,is_read=False).exists())
        self.assertTrue(Notification.objects.filter(user=self.owner,is_read=False).exists())
