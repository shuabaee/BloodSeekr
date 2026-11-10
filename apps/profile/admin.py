from django.contrib import admin

from .models import Profile
from django import forms
from apps.shared.widgets import LocationField,LegacyLocationMixin
from apps.shared.locations import display_location

class ProfileAdminForm(LegacyLocationMixin,forms.ModelForm):
    location=LocationField(max_length=150,required=False)
    class Meta:
        model=Profile
        fields="__all__"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form=ProfileAdminForm
    list_display = ("user", "blood_type", "location_label", "available_to_donate", "is_verified")
    search_fields = ("user__username", "user__email", "location")
    list_filter = ("blood_type", "available_to_donate", "is_verified")

    @admin.display(description="Location")
    def location_label(self,obj):
        return display_location(obj.location)
