from django import template

from apps.blood_data.services import donors_for, recipients_for

register = template.Library()


@register.filter
def donor_types(code):
    """Blood types that can donate to a recipient: {{ item.required_blood_type_id|donor_types }}."""
    return donors_for(str(code or ''))


@register.filter
def recipient_types(code):
    """Blood types a donor can give to: {{ profile.blood_type_id|recipient_types }}."""
    return recipients_for(str(code or ''))
