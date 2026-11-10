from django import forms
from django.contrib import admin
from apps.shared.widgets import LocationField,LegacyLocationMixin
from apps.shared.locations import city_name,display_location,unpack
from .models import Facility
class FacilityAdminForm(LegacyLocationMixin,forms.ModelForm):
    city=forms.CharField(required=False)
    facility_type=forms.ChoiceField(choices=[('hospital','Hospital'),('blood_center','Blood center'),('clinic','Clinic')])
    address=LocationField(max_length=255,label='Collection address')
    class Meta:
        model=Facility
        fields='__all__'
    def save(self,commit=True):
        item=super().save(commit=False)
        if unpack(item.address)["country"]:item.city=city_name(item.address)[:100]
        if commit:item.save()
        return item
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    form=FacilityAdminForm
    list_display=('name','facility_type','city','is_verified')
    list_filter=('city','facility_type','is_verified')
    search_fields=('name','city')
