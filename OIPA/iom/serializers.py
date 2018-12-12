from rest_framework import serializers

from iati import models as iati_models
from api.generics.serializers import DynamicFieldsSerializer
from api.activity.serializers \
    import ActivitySerializer as ParentActivitySerializer

from iom.models import ProjectType


class ProjectTypeSerializer(DynamicFieldsSerializer):
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectType

    def get_code(self, obj):
        return obj.sector.code

    def get_name(self, obj):
        return obj.sector.name


class ActivitySerializer(ParentActivitySerializer):
    projecttype = ProjectTypeSerializer(read_only=True)

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'reporting_organisation',
            'title',
            'descriptions',
            'participating_organisations',
            'other_identifier',
            'activity_status',
            'activity_dates',
            'contact_info',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'locations',
            'sectors',
            'country_budget_items',
            'humanitarian',
            'humanitarian_scope',
            'policy_markers',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            'planned_disbursements',
            'budgets',
            'capital_spend',
            'transactions',
            'document_links',
            'related_activities',
            'legacy_data',
            'conditions',
            'results',
            'crs_add',
            'fss',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'humanitarian',
            'hierarchy',
            'linked_data_uri',
            'secondary_reporter',
            'aggregations',
            'dataset',
            'publisher',
            'published_state',
            'projecttype'
        )

        validators = []
