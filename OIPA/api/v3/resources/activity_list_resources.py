# Tastypie specific
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS

# Data specific
from iati.models import Activity
from api.v3.resources.helper_resources import TitleResource, DescriptionResource, FinanceTypeResource
from api.cache import NoTransformCache
from api.v3.resources.advanced_resources import OnlyCountryResource, OnlyRegionResource
from api.v3.resources.activity_view_resources import ActivityViewParticipatingOrganisationResource, \
    ActivityViewTiedStatusResource, ActivityViewAidTypeResource, ActivityViewOrganisationResource, \
    ActivityViewActivityStatusResource,ActivityViewActivityScopeResource, ActivityViewSectorResource, \
    ActivityViewCollaborationTypeResource, ActivityViewFlowTypeResource, ActivityViewCurrencyResource
from api.v3.resources.helper_resources import DocumentResource

#csv serializer
from api.v3.resources.csv_serializer import CsvSerializer
from activity_view_resources import ActivityResource

from api.paginator import NoCountPaginator

class ActivityListResource(ActivityResource):

    reporting_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'reporting_organisation', full=True, null=True)
    participating_organisations = fields.ToManyField(ActivityViewParticipatingOrganisationResource, 'participating_organisations', full=True, null=True)
    activity_status = fields.ForeignKey(ActivityViewActivityStatusResource, 'activity_status', full=True, null=True)
    activity_scope = fields.ForeignKey(ActivityViewActivityScopeResource, 'scope', full=True, null=True)
    countries = fields.ToManyField(OnlyCountryResource, 'recipient_country', full=True, null=True)
    regions = fields.ToManyField(OnlyRegionResource, 'recipient_region', full=True, null=True)
    sectors = fields.ToManyField(ActivityViewSectorResource, 'sector', full=True, null=True)
    titles = fields.ToManyField(TitleResource, 'title_set', full=True, null=True)
    descriptions = fields.ToManyField(DescriptionResource, 'description_set', full=True, null=True)
    collaboration_type = fields.ForeignKey(ActivityViewCollaborationTypeResource, attribute='collaboration_type', full=True, null=True)
    default_flow_type = fields.ForeignKey(ActivityViewFlowTypeResource, attribute='default_flow_type', full=True, null=True)
    default_finance_type = fields.ForeignKey(FinanceTypeResource, attribute='default_finance_type', full=True, null=True)
    default_aid_type = fields.ForeignKey(ActivityViewAidTypeResource, attribute='default_aid_type', full=True, null=True)
    default_tied_status = fields.ForeignKey(ActivityViewTiedStatusResource, attribute='default_tied_status', full=True, null=True)
    default_currency = fields.ForeignKey(ActivityViewCurrencyResource, attribute='default_currency', full=True, null=True)
    documents = fields.ToManyField(DocumentResource, 'documentlink_set', full=True, null=True)

    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'activity-list'
        max_limit = 100
        excludes = ['date_created']
        serializer = CsvSerializer()
        ordering = ['start_actual', 'start_planned', 'end_actual', 'end_planned', 'sectors', 'total_budget', 'activity_status']
        filtering = {
            'id': ('iregex'),
            'iati_identifier': 'exact',
            'start_planned': ALL,
            #'start_actual': ALL,
            'end_planned': ALL,
            'end_actual': ALL,
            'total_budget': ALL,
            'activity_scope': ('exact', 'in'),
            'sectors': ('exact', 'in'),
            'regions': ALL_WITH_RELATIONS,
            'countries': ALL_WITH_RELATIONS,
            'reporting_organisation': ('exact', 'in'),
            'participating_organisation': ALL,
            'participating_organisations': ALL_WITH_RELATIONS
        }
        cache = NoTransformCache()
        allowed_methods = ['get']
        paginator_class = NoCountPaginator

