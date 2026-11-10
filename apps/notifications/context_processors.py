from .models import Notification
def notification_count(request):
    return {'unread_count':Notification.objects.filter(user=request.user,is_read=False).count() if request.user.is_authenticated else 0}


def map_configuration(request):
    from django.conf import settings
    return {'maps_config':{'google_key':settings.GOOGLE_MAPS_BROWSER_KEY,'map_id':settings.GOOGLE_MAPS_MAP_ID}}
