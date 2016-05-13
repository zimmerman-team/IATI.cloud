from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import TogetherFilterSet
from rest_framework import filters

from iati.models import Location

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D


class DistanceFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        location_longitude = request.query_params.get('location_longitude', None)
        location_latitude = request.query_params.get('location_latitude', None)
        distance_km = request.query_params.get('location_distance_km', None)
        
        if location_longitude and location_latitude and distance_km:
            pnt = GEOSGeometry('POINT({0} {1})'.format(location_longitude, location_latitude))            
            return queryset.filter(point_pos__distance_lte=(pnt, D(km=distance_km)))

        return queryset


class LocationFilter(TogetherFilterSet):


    class Meta:
        model = Location

