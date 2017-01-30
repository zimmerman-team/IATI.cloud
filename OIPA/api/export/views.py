from rest_framework.generics import ListAPIView
from iati.models import Activity
from api.export import serializers as export_serializers
from api.activity import filters
from api.generics.filters import SearchFilter
from api.generics.utils import get_serializer_fields
from common.util import difference
from rest_framework.filters import DjangoFilterBackend
from api.renderers import XMLRenderer
from rest_framework.renderers import BrowsableAPIRenderer
from api.pagination import IatiXMLPagination, IatiXMLUnlimitedPagination
from django.db.models import Q

from rest_framework import authentication, permissions
from api.publisher.permissions import OrganisationAdminGroupPermissions, ActivityCreatePermissions, PublisherPermissions

class IATIActivityList(ListAPIView):

    """IATI representation for activities"""
        
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, filters.RelatedOrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = export_serializers.ActivityXMLSerializer
    pagination_class = IatiXMLPagination

    renderer_classes = (BrowsableAPIRenderer, XMLRenderer )

    fields = difference(
        get_serializer_fields(serializer_class),
        ['url', 'activity_aggregation', 'child_aggregation', 'activity_plus_child_aggregation']
    )

    ordering_fields = (
        'title',
        'planned_start_date',
        'actual_start_date',
        'planned_end_date',
        'actual_end_date',
        'start_date',
        'end_date',
        'activity_budget_value',
        'activity_incoming_funds_value',
        'activity_disbursement_value',
        'activity_expenditure_value',
        'activity_plus_child_budget_value',
    )

    def get_queryset(self):
        return super(IATIActivityList, self).get_queryset().prefetch_all()


class IATIActivityNextExportList(IATIActivityList):
    """IATI representation for activities"""

    renderer_classes = (XMLRenderer, )

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    pagination_class = IatiXMLUnlimitedPagination

    def get_queryset(self):
        publisher_id = self.kwargs.get('publisher_id')
        queryset = super(IATIActivityNextExportList, self).get_queryset()

        # TODO: set a is_publishing flag in the publisher, and do the publishing in a task queue - 2017-01-27

        # get all published activities, except for the ones that are just modified
        filtered = queryset.filter(ready_to_publish=True, publisher_id=publisher_id)

        return filtered



