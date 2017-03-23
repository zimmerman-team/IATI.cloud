from django_filters import FilterSet
from django_filters import NumberFilter

from api.generics.filters import CharFilter, BooleanFilter

from traceability.models import Chain, ChainLink, ChainNodeError, ChainNode



class ChainFilter(FilterSet):
    includes_activity = CharFilter(name='chainnode__activity__iati_identifier', lookup_type='exact')
    end_node_not_of_reporting_org = CharFilter(name='chainlink__end_node__activity__reporting_organisations__ref', lookup_type='exact', exclude=True)

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


class ChainNodeFilter(FilterSet):
    chain_includes_activity = CharFilter(name='chain__chainnode__activity__iati_identifier', lookup_type='exact')
    chain_includes_activity_of_reporting_org = CharFilter(name='chain__chainnode__activity__reporting_organisations__ref', lookup_type='exact')
    reporting_organisation = CharFilter(name='activity__reporting_organisations__ref', lookup_type='exact')
    reporting_organisation_not = CharFilter(name='activity__reporting_organisations__ref', lookup_type='exact', exclude=True)
    is_start_node = BooleanFilter(name='start_link', lookup_type='isnull', distinct=True)
    tier = NumberFilter(name='tier')
    link_end_node_hierarchy = NumberFilter(name='start_link__end_node__activity__hierarchy', lookup_type='exact')
    class Meta:
        model = ChainNode
        fields = [
            'chain_includes_activity',
            'chain_includes_activity_of_reporting_org',
            'reporting_organisation',
            'reporting_organisation_not',
            'is_start_node',
            'tier',
            'link_end_node_hierarchy',
        ]


