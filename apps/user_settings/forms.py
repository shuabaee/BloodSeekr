from django import forms
from .models import UserSettings
class UserSettingsForm(forms.ModelForm):
    match_radius_km = forms.IntegerField(min_value=1, max_value=500, label='Matching radius (km)', help_text='Used for coordinates. Text locations match the same locality only.')
    class Meta:
        model = UserSettings
        fields = ['email_notifications', 'emergency_notifications', 'show_donor_profile', 'match_radius_km']
