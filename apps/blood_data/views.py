from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import BloodType
from .services import compatibility_map


@login_required
def guide(request):
    """Interactive blood type compatibility guide."""
    types = list(BloodType.objects.values_list('code', flat=True))
    matrix = compatibility_map()
    profile = getattr(request.user, 'bloodseekr_profile', None)
    mine = getattr(profile, 'blood_type_id', '') or ''
    rows = [{'donor': donor, 'cells': [{'recipient': r, 'ok': r in matrix.get(donor, [])} for r in types]} for donor in types]
    return render(request, 'blood_data/guide.html', {
        'types': types, 'rows': rows, 'matrix': matrix, 'my_type': mine,
    })
