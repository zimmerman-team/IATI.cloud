# Django specific
from django.db.models import Q

# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

# Data specific
from IATI.models import activity, organisation
from API.v3.resources.helper_resources import *
from API.cache import NoTransformCache
from API.v3.resources.advanced_resources import *

class ActivityViewAidTypeResource(ModelResource):
    class Meta:
        queryset = aid_type.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewFlowTypeResource(ModelResource):
    class Meta:
        queryset = flow_type.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewSectorResource(ModelResource):
    class Meta:
        queryset = sector.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewCollaborationTypeResource(ModelResource):
    class Meta:
        queryset = collaboration_type.objects.all()
        include_resource_uri = False
        excludes = ['description', 'language']

class ActivityViewTiedStatusResource(ModelResource):
    class Meta:
        queryset = tied_status.objects.all()
        include_resource_uri = False
        excludes = ['description']

class ActivityViewOrganisationResource(ModelResource):

    class Meta:
        queryset = organisation.objects.all()
        include_resource_uri = False
        excludes = ['abbreviation', 'reported_by_organisation']
        filtering = {
            'iati_identifier': 'exact'
        }


class ActivityViewTransactionResource(ModelResource):
    provider_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'provider_organisation', full=True, null=True)
    receiver_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'receiver_organisation', full=True, null=True)

    class Meta:
        queryset = transaction.objects.all()
        include_resource_uri = False
        excludes = ['id', 'ref', 'description', 'provider_activity']

    def dehydrate(self, bundle):

        bundle.data['disbursement_channel'] = bundle.obj.disbursement_channel_id
        bundle.data['currency'] = bundle.obj.currency_id
        bundle.data['tied_status'] = bundle.obj.tied_status_id
        bundle.data['transaction_type'] = bundle.obj.transaction_type_id
        return bundle

class ActivityViewActivityStatusResource(ModelResource):
    class Meta:
        queryset = activity_status.objects.all()
        include_resource_uri = False
        excludes = ['language']

# class ActivityViewRecipientCountryResource(ModelResource):
#     class Meta:
#         queryset = activity_recipient_country.objects.all()
#         include_resource_uri = False
#         excludes = ['id']
#
#     def dehydrate(self, bundle):
#         bundle.data['country'] = bundle.obj.code
#         return bundle


class ActivityResource(ModelResource):

    iati_identifier = fields.CharField('id')
    reporting_organisation = fields.ForeignKey(ActivityViewOrganisationResource, 'reporting_organisation', full=True, null=True)
    participating_organisations = fields.ToManyField(ActivityViewOrganisationResource, 'participating_organisation', full=True, null=True)
    activity_status = fields.ForeignKey(ActivityViewActivityStatusResource, 'activity_status', full=True, null=True)
    recipient_country = fields.ToManyField(OnlyCountryResource, 'recipient_country', full=True, null=True)
    recipient_region = fields.ToManyField(OnlyRegionResource, 'recipient_region', full=True, null=True)
    sectors = fields.ToManyField(ActivityViewSectorResource, 'sector', full=True, null=True)
    titles = fields.ToManyField(TitleResource, 'title_set', full=True, null=True)
    descriptions = fields.ToManyField(DescriptionResource, 'description_set', full=True, null=True)
    collaboration_type = fields.ForeignKey(ActivityViewCollaborationTypeResource, attribute='collaboration_type', full=True, null=True)
    default_flow_type = fields.ForeignKey(ActivityViewFlowTypeResource, attribute='default_flow_type', full=True, null=True)
    default_finance_type = fields.ForeignKey(FinanceTypeResource, attribute='default_finance_type', full=True, null=True)
    default_aid_type = fields.ForeignKey(ActivityViewAidTypeResource, attribute='default_aid_type', full=True, null=True)
    default_tied_status = fields.ForeignKey(ActivityViewTiedStatusResource, attribute='default_tied_status', full=True, null=True)
    budget = fields.ToManyField(ActivityBudgetResource, 'budget_set', full=True, null=True)
    transactions = fields.ToManyField(ActivityViewTransactionResource, 'transaction_set', full=True, null=True)
    documents = fields.ToManyField(DocumentResource, 'document_link_set', full=True, null=True)

    class Meta:
        queryset = activity.objects.all()
        resource_name = 'activities'
        max_limit = 100
        serializer = Serializer(formats=['xml', 'json'])
        excludes = ['date_created', 'id']
        ordering = ['start_actual', 'start_planned', 'end_actual', 'end_planned', 'activity_sectors', 'statistics']
        filtering = {
            'iati_identifier': ALL,
            'start_planned': ALL,
            'start_actual': ALL,
            'end_planned' : ALL,
            'end_actual' : ALL

        }
        cache = NoTransformCache()

    # def dehydrate(self, bundle):
    #     bundle.data['recipient_country'] = "test"
    #     print bundle.obj.recipient_country.country.code
    #     return bundle

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(ActivityResource, self).apply_filters(request, applicable_filters)
        query = request.GET.get('query', None)
        sectors = request.GET.get('sectors', None)
        regions = request.GET.get('regions', None)
        countries = request.GET.get('countries', None)
        organisations = request.GET.get('organisations', None)
        filters = {}
        if sectors:
            sectors = sectors.replace('|', ',').split(',')
            filters.update(dict(activity_sector__sector__code__in=sectors))
        if regions:
            regions = regions.replace('|', ',').split(',')
            filters.update(dict(activity_recipient_region__region__code__in=regions))
        if countries:
            countries = countries.replace('|', ',').split(',')
            filters.update(dict(activity_recipient_country__country__code__in=countries))
        if organisations:
            organisations = organisations.replace('|', ',').split(',')
            filters.update(dict(reporting_organisation__code__in=organisations))
        if query:

            qset = (
                Q(id__in=query, **filters) |
                Q(activity_recipient_country__country__name__in=query, **filters) |
                Q(title__title__icontains=query, **filters) |
                Q(description__description__icontains=query, **filters)
            )

            return base_object_list.filter(qset).distinct()
        return base_object_list.filter(**filters).distinct()







