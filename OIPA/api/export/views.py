from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import GenericAPIView
from iati.models import Activity
from api.activity import serializers as activity_serializers
from api.activity import filters
from api.activity.filters import SearchFilter
from api.generics.views import DynamicListView, DynamicDetailView
from api.generics.utils import get_serializer_fields
from common.util import difference

from rest_framework.filters import DjangoFilterBackend

from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter
from api.renderers import XMLRenderer

from rest_framework.response import Response
from rest_framework import mixins, status

print(difference(
    get_serializer_fields(activity_serializers.ActivitySerializer),
    ['url', 'activity_aggregation', 'child_aggregation', 'activity_plus_child_aggregation']
    )
)

class IATIActivityList(ListAPIView):

    """IATI representation for activities"""
        
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, filters.RelatedOrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = activity_serializers.ActivityXMLSerializer

    renderer_classes = (XMLRenderer, )

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
        qs = super(IATIActivityList, self).get_queryset()
        return qs.distinct('id')


