# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

# Data specific
from api.cache import NoTransformCache
from iati.models import ContactInfo, Activity, Organisation, AidType, FlowType, Sector, CollaborationType, \
    TiedStatus, Transaction, ActivityStatus, Currency, OrganisationRole, ActivityScope, \
    ActivityParticipatingOrganisation, Location, Result
from api.v3.resources.helper_resources import TitleResource, DescriptionResource, FinanceTypeResource, \
    ActivityBudgetResource, DocumentResource, WebsiteResource, PolicyMarkerResource, OtherIdentifierResource
from api.v3.resources.advanced_resources import OnlyCountryResource, OnlyRegionResource

# cache specific
from django.http import HttpResponse
from cache.validator import Validator

from api.v3.resources.csv_serializer import CsvSerializer
from api.api_tools import comma_separated_parameter_to_list

from api.paginator import NoCountPaginator

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

class ActivityViewCurrencyResource(ModelResource):
    class Meta:
        queryset = Currency.objects.all()
        include_resource_uri = False
        excludes = ['language']

class ActivityViewContactInfoResource(ModelResource):
    class Meta:
        queryset = ContactInfo.objects.all()
        include_resource_uri = False
        excludes = ['id']



class ActivityLocationResource(ModelResource):

    class Meta:
        queryset = Location.objects.all()
        include_resource_uri = False
        excludes = ['id', 'activity_description', 'adm_code', 'adm_country_adm1', 'adm_country_adm2',
                    'adm_country_name', 'adm_level', 'gazetteer_entry', 'location_id_code', 'point_srs_name',
                    'ref', 'type_description', 'point_pos']


class ActivityResultResource(ModelResource):

    class Meta:
        queryset = Result.objects.all()
        include_resource_uri = False
        excludes = ['id']

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
    other_identifier = fields.ToManyField(OtherIdentifierResource, 'otheridentifier_set', full=True, null=True, use_in='detail')
    locations = fields.ToManyField(ActivityLocationResource, 'location_set', full=True, null=True, use_in='all')
    results = fields.ToManyField(ActivityResultResource, 'result_set', full=True, null=True, use_in='detail')
    # to add:
    # conditions
    # contact
    # country-budget?
    # crsadd
    # disbursement channel?
    # ffs
    # ffs forecast?
    # planned disbursement
    # related activity
    # verification status
    # vocabulary?


    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'activities'
        max_limit = 1000
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
        paginator_class = NoCountPaginator


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

    def full_dehydrate(self, bundle, for_list=False):
        #If the select_fields param is found, run this overwritten method.
        #Otherwise run the default Tastypie method
        select_fields_param = bundle.request.GET.get('select_fields', None)
        if select_fields_param:
            select_fields = comma_separated_parameter_to_list(select_fields_param)
            for field_name, field_object in self.fields.items():
                #If the field_name is in the list of requested fields dehydrate it
                if (field_name) in select_fields:

                    # A touch leaky but it makes URI resolution work.
                    if getattr(field_object, 'dehydrated_type', None) == 'related':
                        field_object.api_name = self._meta.api_name
                        field_object.resource_name = self._meta.resource_name

                    bundle.data[field_name] = field_object.dehydrate(bundle, for_list=for_list)

                    # Check for an optional method to do further dehydration.
                    method = getattr(self, "dehydrate_%s" % field_name, None)

                    if method:
                        bundle.data[field_name] = method(bundle)

            bundle = self.dehydrate(bundle)
            return bundle
        else:
            return super(ActivityResource, self).full_dehydrate(bundle, for_list)

    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')
        else:
            return super(ActivityResource, self).get_list(request, **kwargs)

    def alter_list_data_to_serialize(self, request, data):
        select_fields_param = request.GET.get('select_fields', None)
        if select_fields_param:
            select_fields = comma_separated_parameter_to_list(select_fields_param)
            data['meta']['selectable_fields'] = {f[0] for f in self.fields.items()} - {f for f in select_fields}
        return data
