from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response


@api_view(('GET',))
def welcome(request, format=None):
    """
    # REST API

    The REST API provides programmatic access to read and write IATI data.
    Fetch IATI Activity, Transaction or other IATI data.
    The REST API responses are available in JSON.

    ## Available endpoints

    * Activities: [`/api/activities`](/api/activities)

    * Sectors: [`/api/sectors`](/api/sectors)

    * Organisations: [`/api/organisations`](/api/organisations)

    * Transactions: [`/api/transactions`](/api/transactions)

    * Regions: [`/api/regions`](/api/regions)

    * Countries: [`/api/countries`](/api/countries)

    * Cities: [`/api/cities`](/api/cities)

    """
    return Response({
        'endpoints': {
            'cities': reverse(
                'city-list',
                request=request,
                format=format),
            'regions': reverse(
                'region-list',
                request=request,
                format=format),
            'activities': reverse(
                'activity-list',
                request=request,
                format=format),
            'countries': reverse(
                'country-list',
                request=request,
                format=format),
            'sectors': reverse(
                'sector-list',
                request=request,
                format=format),
            'organisations': reverse(
                'organisation-list',
                request=request,
                format=format),
            'transactions': reverse(
                'transactions:list',
                request=request,
                format=format),
        }
    })
