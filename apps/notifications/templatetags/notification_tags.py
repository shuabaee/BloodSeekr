from django import template

register = template.Library()

ICONS = {
    'matching_request': 'droplet', 'donor_response': 'users', 'response_update': 'check-circle',
    'request_status': 'info', 'collection_update': 'pin', 'donation_record': 'heart',
}


@register.filter
def notice_icon(kind):
    return ICONS.get(kind, 'bell')
