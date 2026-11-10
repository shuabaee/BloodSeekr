from django import template
from apps.shared.locations import display_location,directions_url
register=template.Library()
register.filter('location_label',display_location)
register.filter('directions_url',directions_url)
