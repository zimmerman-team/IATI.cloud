# Django specific
from django.db.models import Q

# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

# Data specific
from api.cache import NoTransformCache
from iati.models import Activity, Organisation, AidType, FlowType, Sector, CollaborationType, TiedStatus, Transaction, ActivityStatus, Currency, OrganisationRole, ActivityScope, ActivityParticipatingOrganisation
from api.v3.resources.helper_resources import TitleResource, DescriptionResource, FinanceTypeResource, ActivityBudgetResource, DocumentResource, WebsiteResource, PolicyMarkerResource, OtherIdentifierResource
from api.v3.resources.advanced_resources import OnlyCountryResource, OnlyRegionResource

# cache specific
from django.http import HttpResponse
from cache.validator import Validator

from api.v3.resources.csv_serializer import CsvSerializer
from api.dev.api_tools import comma_separated_parameter_to_list

class ActivityViewAidTypeResource(ModelResource):
    class Meta:
        queryset = AidType.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewFlowTypeResource(ModelResource):
    class Meta:
        queryset = FlowType.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewSectorResource(ModelResource):
    class Meta:
        queryset = Sector.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewCollaborationTypeResource(ModelResource):
    class Meta:
        queryset = CollaborationType.objects.all()
        include_resource_uri = False
        excludes = ['description', 'language']

class ActivityViewTiedStatusResource(ModelResource):
    class Meta:
        queryset = TiedStatus.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewOrganisationRoleResource(ModelResource):
    class Meta:
        queryset = OrganisationRole.objects.all()
        include_resource_uri = False



class ActivityViewOrganisationResource(ModelResource):
    organisation_role = fields.ForeignKey(ActivityViewOrganisationRoleResource, 'organisation_role', full=True, null=True)


    class Meta:
        queryset = Organisation.objects.all()
        include_resource_uri = False
        excludes = ['abbreviation', 'reported_by_organisation']
        filtering = {
            'iati_identifier': 'exact',
            'code': ALL_WITH_RELATIONS
        }






class ActivityViewTransactionResource(ModelResource):
    provider_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'provider_organisation', full=True, null=True)
    receiver_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'receiver_organisation', full=True, null=True)

    class Meta:
        queryset = Transaction.objects.all()
        include_resource_uri = False
        excludes = ['id', 'ref', 'description', 'provider_activity']
        allowed_methods = ['get']

    def dehydrate(self, bundle):

        bundle.data['disbursement_channel'] = bundle.obj.disbursement_channel_id
        bundle.data['currency'] = bundle.obj.currency_id
        bundle.data['tied_status'] = bundle.obj.tied_status_id
        bundle.data['transaction_type'] = bundle.obj.transaction_type_id
        return bundle



class ActivityViewParticipatingOrganisationResource(ModelResource):
    organisation = fields.ToOneField(ActivityViewOrganisationResource, 'organisation', full=True, null=True)

    class Meta:
        queryset = ActivityParticipatingOrganisation.objects.all()
        include_resource_uri = False
        excludes = ['id']
        filtering = {
            'organisation': ALL_WITH_RELATIONS
        }

    def dehydrate(self, bundle):
        bundle.data['role_id'] = bundle.obj.role_id
        bundle.data['code'] = bundle.obj.organisation_id
        return bundle



class ActivityViewActivityStatusResource(ModelResource):
    class Meta:
        queryset = ActivityStatus.objects.all()
        include_resource_uri = False
        excludes = ['language']

class ActivityViewActivityScopeResource(ModelResource):
    class Meta:
        queryset = ActivityScope.objects.all()
        include_resource_uri = False
2

class ActivityViewCurrencyResource(ModelResource):
    class Meta:
        queryset = Currency.objects.all()
        include_resource_uri = False
        excludes = ['language']








class ActivityResource(ModelResource):
    countries = fields.ToManyField(OnlyCountryResource, 'recipient_country', full=True, null=True, use_in='all')
    regions = fields.ToManyField(OnlyRegionResource, 'recipient_region', full=True, null=True, use_in='all')
    sectors = fields.ToManyField(ActivityViewSectorResource, 'sector', full=True, null=True, use_in='all')
    titles = fields.ToManyField(TitleResource, 'title_set', full=True, null=True, use_in='all')
    descriptions = fields.ToManyField(DescriptionResource, 'description_set', full=True, null=True, use_in='all')
    participating_organisations = fields.ToManyField(ActivityViewOrganisationResource, 'participating_organisation', full=True, null=True, use_in='all')
    reporting_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'reporting_organisation', full=True, null=True, use_in='detail' )
    activity_status = fields.ForeignKey(ActivityViewActivityStatusResource, 'activity_status', full=True, null=True, use_in='detail')
    websites = fields.ToManyField(WebsiteResource, 'activity_website_set', full=True, null=True, use_in='detail')
    policy_markers = fields.ToManyField(PolicyMarkerResource, 'policy_marker', full=True, null=True, use_in='detail')
    collaboration_type = fields.ForeignKey(ActivityViewCollaborationTypeResource, attribute='collaboration_type', full=True, null=True, use_in='detail')
    default_flow_type = fields.ForeignKey(ActivityViewFlowTypeResource, attribute='default_flow_type', full=True, null=True, use_in='detail')
    default_finance_type = fields.ForeignKey(FinanceTypeResource, attribute='default_finance_type', full=True, null=True, use_in='detail')
    default_aid_type = fields.ForeignKey(ActivityViewAidTypeResource, attribute='default_aid_type', full=True, null=True, use_in='detail')
    default_tied_status = fields.ForeignKey(ActivityViewTiedStatusResource, attribute='default_tied_status', full=True, null=True, use_in='detail')
    activity_scope = fields.ForeignKey(ActivityViewActivityScopeResource, attribute='scope', full=True, null=True, use_in='detail')
    default_currency = fields.ForeignKey(ActivityViewCurrencyResource, attribute='default_currency', full=True, null=True, use_in='detail')
    budget = fields.ToManyField(ActivityBudgetResource, 'budget_set', full=True, null=True, use_in='detail')
    transactions = fields.ToManyField(ActivityViewTransactionResource, 'transaction_set', full=True, null=True, use_in='detail')
    documents = fields.ToManyField(DocumentResource, 'documentlink_set', full=True, null=True, use_in='detail')

    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'activities'
        max_limit = 100
        serializer = CsvSerializer()
        excludes = ['date_created']
        ordering = ['start_actual', 'start_planned', 'end_actual', 'end_planned', 'sectors', 'total_budget']
        filtering = {
            'iati_identifier': 'exact',
            'start_planned': ALL,
            'start_actual': ALL,
            'end_planned': ALL,
            'end_actual': ALL,
            'total_budget': ALL,
            'sectors': ('exact', 'in'),
            'regions': ('exact', 'in'),
            'countries': ('exact', 'in'),
            'reporting_organisation': ('exact', 'in'),
            'documents': ALL_WITH_RELATIONS
        }
        cache = NoTransformCache()


    def apply_filters(self, request, applicable_filters):
        activity_list = super(ActivityResource, self).apply_filters(request, applicable_filters).prefetch_related('title_set').prefetch_related('description_set')
        query = request.GET.get('query', None)
        filter_year_param = request.GET.get('start_year_planned__in', None)

        if query:
            search_fields = comma_separated_parameter_to_list(request.GET.get('search_fields', None))
            activity_list = activity_list.search(query, search_fields)

        if filter_year_param:
            years = comma_separated_parameter_to_list(filter_year_param)
            activity_list = activity_list.filter_years(years)

        return activity_list.distinct_if_necessary(applicable_filters)

    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')
        else:
            return super(ActivityResource, self).get_list(request, **kwargs)