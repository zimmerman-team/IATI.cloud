from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from django.db import connections
from django.db import OperationalError


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

    # Legacy API

    Legacy API (v3) is still accesseble but will be depricated soon.

    [`/api/v3/docs/`](/api/v3/docs/)

    """
    return Response({
        'endpoints': {
            'cities': reverse(
                'cities:city-list',
                request=request,
                format=format),
            'regions': reverse(
                'regions:region-list',
                request=request,
                format=format),
            'activities': reverse(
                'activities:activity-list',
                request=request,
                format=format),
            'countries': reverse(
                'countries:country-list',
                request=request,
                format=format),
            'sectors': reverse(
                'sectors:sector-list',
                request=request,
                format=format),
            'organisations': reverse(
                'organisations:organisation-list',
                request=request,
                format=format),
            'transactions': reverse(
                'transactions:list',
                request=request,
                format=format),
        }
    })


@api_view(('GET',))
def health_check(request, format=None):
    """
    Performs an API health check
    """
    print('called')
    okay = True

    conn = connections['default']
    try:
        c = conn.cursor()
    except OperationalError:
        okay = False

    if okay is False:
        return Response(status=500)

    return Response(status=200)
