from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .locations import catalog
@require_GET
def location_options(request):
    country=request.GET.get('country','PH')
    data=catalog().get(country)
    if not data:return JsonResponse({'error':'Unknown country.'},status=400)
    region=request.GET.get('province','')
    cities=[x for x in data['cities'] if not region or x['region']==region]
    response=JsonResponse({'country':country,'name':data['name'],'regions':[{'id':k,'name':v} for k,v in sorted(data['regions'].items(),key=lambda x:x[1])],'cities':cities})
    response['Cache-Control']='public, max-age=86400'
    return response


# --- Friendly error pages (shared; every feature raises PermissionDenied / Http404) ---
from django.http import HttpResponse
from django.shortcuts import render


def _error(request, status, title, message, icon):
    user = getattr(request, 'user', None)
    layout = 'shared/base.html' if user is not None and user.is_authenticated else 'shared/plain.html'
    context = {'status': status, 'title': title, 'message': message, 'icon': icon, 'layout': layout}
    try:
        return render(request, 'shared/error.html', context, status=status)
    except Exception:  # e.g. database unavailable while building the navigation
        return HttpResponse(f'{title}. {message}', status=status, content_type='text/plain')


def permission_denied(request, exception=None):
    detail = str(exception) if exception and str(exception) else ''
    return _error(request, 403, "You don't have access to this page", detail or 'This page is only available to its owner, matching donors or staff.', 'lock')


def page_not_found(request, exception=None):
    return _error(request, 404, "We couldn't find that page", 'The link may be old or the item may have been removed.', 'search')


def server_error(request):
    return _error(request, 500, 'Something went wrong on our side', 'Please try again in a moment. If it keeps happening, let an administrator know.', 'alert')
