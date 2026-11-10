from django.contrib import admin

from .models import BloodType


@admin.register(BloodType)
class BloodTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "abo_group", "rh_factor", "display_name")
    search_fields = ("code", "display_name")
