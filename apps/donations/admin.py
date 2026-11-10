from django.contrib import admin
from .models import DonationRecord
@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ('donor_response','facility','donation_date','units_donated','screening_status','donation_status')
    list_filter = ('screening_status','donation_status')
    def has_add_permission(self,request):
        return False
    def has_change_permission(self,request,obj=None):
        return False
