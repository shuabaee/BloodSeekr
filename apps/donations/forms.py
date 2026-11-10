from django import forms
from django.utils import timezone
from .models import DonationRecord
class DonationForm(forms.ModelForm):
    units_donated = forms.DecimalField(max_digits=4,decimal_places=2,min_value=0,max_value=99.99)
    screening_status = forms.ChoiceField(choices=[('pending','Pending'),('passed','Passed'),('failed','Failed')])
    donation_status = forms.ChoiceField(choices=[('scheduled','Scheduled'),('completed','Completed'),('cancelled','Cancelled')])
    class Meta:
        model = DonationRecord
        fields = ['facility','donation_date','units_donated','screening_status','donation_status']
        widgets = {'donation_date':forms.DateInput(attrs={'type':'date'},format='%Y-%m-%d')}
    def clean(self):
        data = super().clean()
        if data.get('donation_status') == 'completed':
            if data.get('screening_status') != 'passed':
                self.add_error('screening_status','Completed donations require passed screening.')
            if data.get('units_donated') is not None and data['units_donated'] <= 0:
                self.add_error('units_donated','Completed donations require positive units.')
            if data.get('donation_date') and data['donation_date'] > timezone.localdate():
                self.add_error('donation_date','Completed donations cannot be dated in the future.')
        return data
