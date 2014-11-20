from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'cities': reverse('city-list', request=request, format=format),
        'regions': reverse('region-list', request=request, format=format),
        'activities': reverse('activity-list', request=request, format=format),
        'countries': reverse('country-list', request=request, format=format),
        'sectors': reverse('sector-list', request=request, format=format),
        'organisations': reverse(
            'organisation-list', request=request, format=format
        ),
    })
