from django_filters import FilterSet
from django_filters import NumberFilter

from api.generics.filters import CharFilter

from traceability.models import Chain, ChainLink, ChainNodeError



class ChainFilter(FilterSet):
    includes_activity = CharFilter(name='chainnode__activity__iati_identifier', lookup_type='exact')

    class Meta:
        model = Chain
        fields = ['includes_activity']


class ChainLinkFilter(FilterSet):

    chain = NumberFilter(name='chain__id')

    class Meta:
        model = ChainLink
        fields = ['chain']


class ChainNodeErrorFilter(FilterSet):
    chain = NumberFilter(name='chain__id')

    class Meta:
        model = ChainNodeError
        fields = ['chain']


