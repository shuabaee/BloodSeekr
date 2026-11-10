from django.core.management.base import BaseCommand
from django.db import transaction
from apps.blood_data.models import BloodType, BloodCompatibility
# Red-cell coordination only. Facility must confirm typing and crossmatch.
# https://www.redcrossblood.org/donate-blood/blood-types.html
COMPATIBLE = {
    'O-': ['O-','O+','A-','A+','B-','B+','AB-','AB+'],
    'O+': ['O+','A+','B+','AB+'], 'A-': ['A-','A+','AB-','AB+'],
    'A+': ['A+','AB+'], 'B-': ['B-','B+','AB-','AB+'],
    'B+': ['B+','AB+'], 'AB-': ['AB-','AB+'], 'AB+': ['AB+'],
}
class Command(BaseCommand):
    help = 'Add missing blood types and compatibility pairs without overwriting existing rows.'
    @transaction.atomic
    def handle(self, *args, **options):
        for code in COMPATIBLE:
            BloodType.objects.get_or_create(code=code, defaults={'abo_group':code[:-1], 'rh_factor':code[-1], 'display_name':code})
        count = 0
        for donor in COMPATIBLE:
            for recipient in COMPATIBLE:
                _, created = BloodCompatibility.objects.get_or_create(donor_blood_type_id=donor, recipient_blood_type_id=recipient, defaults={'is_compatible':recipient in COMPATIBLE[donor]})
                count += created
        self.stdout.write(self.style.SUCCESS(f'Added {count} missing compatibility rows; existing data preserved.'))
