# Django specific
from django.db.models import Q

# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

# Data specific
from iati.models import Activity
from api.v3.resources.helper_resources import TitleResource, DescriptionResource, FinanceTypeResource
from api.cache import NoTransformCache
from api.v3.resources.advanced_resources import OnlyCountryResource, OnlyRegionResource
from api.v3.resources.activity_view_resources import ActivityViewTiedStatusResource, ActivityViewAidTypeResource, ActivityViewOrganisationResource, ActivityViewActivityStatusResource, ActivityViewSectorResource, ActivityViewCollaborationTypeResource, ActivityViewFlowTypeResource, ActivityViewCurrencyResource

#cache specific
from django.http import HttpResponse
from cache.validator import Validator

class ActivityListResource(ModelResource):

    reporting_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'reporting_organisation', full=True, null=True)
    participating_organisations = fields.ToManyField(ActivityViewOrganisationResource, 'participating_organisation', full=True, null=True)
    activity_status = fields.ForeignKey(ActivityViewActivityStatusResource, 'activity_status', full=True, null=True)
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


    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'activity-list'
        max_limit = 100
        serializer = Serializer(formats=['xml', 'json'])
        excludes = ['date_created']
        ordering = ['start_actual', 'start_planned', 'end_actual', 'end_planned', 'sectors', 'total_budget']
        filtering = {
            'iati_identifier': 'exact',
            'start_planned': ALL,
            'start_actual': ALL,
            'end_planned' : ALL,
            'end_actual' : ALL,
            'total_budget': ALL,
            'sectors' : ('exact', 'in'),
            'regions': ('exact', 'in'),
            'countries': ('exact', 'in'),
            'reporting_organisation': ('exact', 'in')
        }
        cache = NoTransformCache()


    def apply_filters(self, request, applicable_filters):
        base_object_list = super(ActivityListResource, self).apply_filters(request, applicable_filters)
        query = request.GET.get('query', None)
        filters = {}
        if query:

            qset = (
                Q(id__in=query, **filters) |
                Q(activityrecipientcountry__country__name__in=query, **filters) |
                Q(title__title__icontains=query, **filters) #|
                # Q(description__description__icontains=query, **filters)
            )

            return base_object_list.filter(qset).distinct()
        return base_object_list.filter(**filters).distinct()

    # def get_list(self, request, **kwargs):
    #
    #     # check if call is cached using validator.is_cached
    #     # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
    #     validator = Validator()
    #     cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']
    #
    #     if not 'flush' in cururl and validator.is_cached(cururl):
    #         return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')
    #     else:
    #         return super(ActivityListResource, self).get_list(request, **kwargs)