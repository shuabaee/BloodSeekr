from django import forms
from django.utils import timezone
from .models import BloodRequest
from apps.shared.widgets import LocationField,LegacyLocationMixin
URGENCIES = [('routine','Routine'),('urgent','Urgent'),('emergency','Emergency')]
class BloodRequestForm(LegacyLocationMixin,forms.ModelForm):
    location = LocationField(max_length=255,label="Collection location",help_text="Use the facility location or choose where donors should attend.")
    units_needed = forms.IntegerField(min_value=1, max_value=32767, widget=forms.NumberInput(attrs={'min': 1, 'inputmode': 'numeric'}), help_text='One unit is about one standard whole-blood donation.')
    urgency = forms.ChoiceField(choices=URGENCIES, widget=forms.Select(attrs={'data-pill-select': 'compact', 'aria-label': 'Urgency'}))
    class Meta:
        model = BloodRequest
        fields = ['required_blood_type','patient_name','units_needed','urgency','needed_date','location','facility']
        widgets = {
            'needed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'required_blood_type': forms.Select(attrs={'data-pill-select': 'compact', 'aria-label': 'Blood type needed'}),
            'patient_name': forms.TextInput(attrs={'placeholder': 'Full name of the patient', 'autocomplete': 'off'}),
        }
    def clean_needed_date(self):
        date = self.cleaned_data['needed_date']
        if date < timezone.localdate():
            raise forms.ValidationError('Needed date cannot be in the past.')
        return date

class DonorResponseForm(forms.Form):
    notes = forms.CharField(required=False, max_length=2000, widget=forms.Textarea(attrs={'rows':3}), help_text='Add your availability or coordination notes.')

class RequestStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[('open','Open'),('in_progress','In progress'),('fulfilled','Fulfilled'),('cancelled','Cancelled')])

class RequestLocationForm(LegacyLocationMixin,forms.ModelForm):
    location=LocationField(max_length=255,label='Collection location')
    class Meta:
        model=BloodRequest
        fields=['facility','location']
