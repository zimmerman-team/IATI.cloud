from django_filters import FilterSet
from django_filters import NumberFilter

from api.generics.filters import CharFilter, BooleanFilter

from traceability.models import Chain, ChainLink, ChainNodeError, ChainNode

from api.generics.filters import CommaSeparatedCharFilter


class IncludesActivityFilter(CharFilter):

    def filter(self, qs, value):
        if value in ([], (), {}, None, ''):
            return qs
        qs = qs.filter(**{'%s__%s' % (self.name, self.lookup_expr): value, '%s__%s' % ('chainnode__treated_as_end_node', 'exact'): False})
        return qs

class ChainFilter(FilterSet):
    includes_activity = IncludesActivityFilter(name='chainnode__activity__iati_identifier', lookup_expr='exact')

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
    reporting_organisation_identifier = CharFilter(name='chain_node__activity__reporting_organisations__organisation__organisation_identifier', lookup_expr='exact')

    class Meta:
        model = ChainNodeError
        fields = ['chain', 'warning_level']

        
class ChainNodeFilter(FilterSet):
    chain_includes_activity = CharFilter(name='chain__chainnode__activity__iati_identifier', lookup_expr='exact')
    chain_includes_activity_of_reporting_organisation_identifier = CommaSeparatedCharFilter(name='chain__chainnode__activity__reporting_organisations__organisation__organisation_identifier', lookup_expr='in')
    reporting_organisation_identifier = CharFilter(name='activity__reporting_organisations__organisation__organisation_identifier', lookup_expr='exact')
    reporting_organisation_identifier_not = CharFilter(name='activity__reporting_organisations__organisation__organisation_identifier', lookup_expr='exact', exclude=True)
    is_start_node = BooleanFilter(name='start_link', lookup_expr='isnull', distinct=True)
    tier = NumberFilter(name='tier')
    link_end_node_hierarchy = NumberFilter(name='start_link__end_node__activity__hierarchy', lookup_expr='exact')
    hierarchy = CharFilter(name='activity__hierarchy', lookup_expr='exact')
    bol = BooleanFilter(name='bol', lookup_expr='exact')
    eol = BooleanFilter(name='eol', lookup_expr='exact')
    treated_as_end_node = BooleanFilter(name='treated_as_end_node', lookup_expr='exact')


    class Meta:
        model = ChainNode
        fields = [
            'chain_includes_activity',
            'chain_includes_activity_of_reporting_organisation_identifier',
            'reporting_organisation_identifier',
            'reporting_organisation_identifier_not',
            'is_start_node',
            'tier',
            'link_end_node_hierarchy',
            'hierarchy',
            'bol',
            'eol',
            'treated_as_end_node',
        ]


