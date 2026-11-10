from django import forms
from apps.shared.widgets import LocationField,LegacyLocationMixin
from apps.shared.locations import city_name,unpack
from .models import Facility
class FacilityForm(LegacyLocationMixin,forms.ModelForm):
    facility_type=forms.ChoiceField(choices=[('hospital','Hospital'),('blood_center','Blood center'),('clinic','Clinic')])
    address=LocationField(max_length=255,label='Collection address',help_text='Place the pin at the facility entrance or donor collection point.')
    class Meta:
        model=Facility
        fields=['name','facility_type','address','contact_phone','contact_email']
    def save(self,commit=True):
        instance=super().save(commit=False)
        city=city_name(instance.address)
        if unpack(instance.address)["country"] and city:instance.city=city[:100]
        if commit:instance.save()
        return instance
