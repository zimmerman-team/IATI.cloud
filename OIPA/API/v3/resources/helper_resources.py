# Tastypie specific
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer

# Data specific
from IATI.models import *


class LanguageResource(ModelResource):
    class Meta:
        queryset = language.objects.all()
        include_resource_uri = False
        excludes = ['id']


class TitleResource(ModelResource):
    language = fields.ToOneField(LanguageResource, 'language', full=True, null=True)
    class Meta:
        queryset = title.objects.all()
        include_resource_uri = False
        excludes = ['id']


class DescriptionResource(ModelResource):
    language = fields.ToOneField(LanguageResource, 'language', full=True, null=True)
    class Meta:
        queryset = description.objects.all()
        include_resource_uri = False
        excludes = ['id']


class OrganisationTypeResource(ModelResource):

    class Meta:
        queryset = organisation_type.objects.all()
        include_resource_uri = False


class ParticipatingOrganisationResource(ModelResource):

    class Meta:
        queryset = activity_participating_organisation.objects.all()
        include_resource_uri = False
        excludes = ['type', 'reported_by_organisation', 'abbreviation']


class ActivityStatusResource(ModelResource):
    class Meta:
        queryset = activity_status.objects.all()
        include_resource_uri = False


class CollaborationTypeResource(ModelResource):
    class Meta:
        queryset = collaboration_type.objects.all()
        include_resource_uri = False


class FlowTypeResource(ModelResource):
    class Meta:
        queryset = flow_type.objects.all()
        include_resource_uri = False


class AidTypeResource(ModelResource):
    class Meta:
        queryset = aid_type.objects.all()
        include_resource_uri = False


class FinanceTypeResource(ModelResource):
    class Meta:
        queryset = finance_type.objects.all()
        include_resource_uri = False


class TiedStatusResource(ModelResource):
    class Meta:
        queryset = tied_status.objects.all()
        include_resource_uri = False

class ActivityBudgetResource(ModelResource):
    class Meta:
        queryset = budget.objects.all()
        include_resource_uri = False
        excludes = ['id']


class TransactionResource(ModelResource):
    class Meta:
        queryset = transaction.objects.all()
        include_resource_uri = False
        filtering = {
            'value': ALL,
            }

class DocumentResource(ModelResource):
    class Meta:
        queryset = document_link.objects.all()
        include_resource_uri = False
        excludes = ['id']


class RecipientCountryResource(ModelResource):
    class Meta:
        queryset = activity_recipient_country.objects.all()
        include_resource_uri =  False


class RecipientRegionResource(ModelResource):
    class Meta:
        queryset = activity_recipient_region.objects.all()
        include_resource_uri = False

class WebsiteResource(ModelResource):
    class Meta:
        queryset = activity_website.objects.all()
        include_resource_uri = False
        excludes = ['id']