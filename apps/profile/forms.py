from django import forms
from django.contrib.auth.models import User

from .models import Profile
from apps.shared.widgets import LocationField,LegacyLocationMixin


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "your@email.com"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        duplicate = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


class ProfileForm(LegacyLocationMixin,forms.ModelForm):
    location = LocationField(max_length=150, required=False, label="Donor location", help_text="Choose your locality, then move the pin or use your current location for more accurate matching.")
    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "blood_type",
            "date_of_birth",
            "location",
            "available_to_donate",
        ]
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "e.g. 0917 123 4567"}),
            "blood_type": forms.Select(attrs={"data-pill-select": "compact", "aria-label": "Blood type"}),
            "date_of_birth": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def clean_date_of_birth(self):
        from django.utils import timezone
        value = self.cleaned_data.get('date_of_birth')
        if value and value >= timezone.localdate():
            raise forms.ValidationError('Date of birth must be in the past.')
        return value

    def clean(self):
        data = super().clean()
        if data.get('available_to_donate'):
            for field in ['blood_type', 'location', 'phone_number']:
                if not data.get(field):
                    self.add_error(field, 'Required when available to donate.')
        return data
