from rest_framework import serializers
from api.generics.serializers import XMLMetaMixin
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import SkipNullMixin

import api.activity.serializers as activity_serializers
import api.transaction.serializers as transaction_serializers

from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.serializers import FilterableModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
# from api.activity.filters import BudgetFilter
from api.activity.filters import RelatedActivityFilter






















class VocabularySerializer(XMLMetaMixin, activity_serializers.VocabularySerializer):
    xml_meta = {'only': 'code'}

class CodelistSerializer(XMLMetaMixin, DynamicFieldsSerializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField()

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer()

# TODO: separate this
class NarrativeSerializer(XMLMetaMixin, activity_serializers.NarrativeSerializer):
    xml_meta = {'attributes': ('xml_lang',)}

    xml_lang = serializers.CharField(source='language.code')

    class Meta(activity_serializers.NarrativeSerializer.Meta):
        fields = ('xml_lang', 'text',)

class NarrativeContainerSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)


class DocumentCategorySerializer(XMLMetaMixin, activity_serializers.DocumentCategorySerializer):
    xml_meta = {'attributes': ('code',)}

    class Meta(activity_serializers.DocumentCategorySerializer.Meta):
        fields = ('code',)


class DocumentLinkSerializer(XMLMetaMixin, activity_serializers.DocumentLinkSerializer):
    xml_meta = {'attributes': ('url', 'format',)}

    format = CodelistSerializer(source='file_format')
    category = DocumentCategorySerializer(many=True, source='categories')
    title = NarrativeContainerSerializer(source="documentlinktitle_set", many=True)

    class Meta(activity_serializers.DocumentLinkSerializer.Meta):
        fields = (
            'url',
            'format',
            'title',
            'category',
        )


class CapitalSpendSerializer(XMLMetaMixin, activity_serializers.CapitalSpendSerializer):
    xml_meta = {'attributes': ('percentage',)}

    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='capital_spend',
        coerce_to_string=False
    )

    class Meta(activity_serializers.CapitalSpendSerializer.Meta):
        fields = ('percentage',)


class BudgetSerializer(XMLMetaMixin, activity_serializers.BudgetSerializer):
    xml_meta = {'attributes': ('type',)}

    class ValueSerializer(serializers.Serializer):
        currency = CodelistSerializer()
        date = serializers.CharField(source='value_date')
        value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
        )

        class Meta(activity_serializers.BudgetSerializer.ValueSerializer.Meta):
            fields = (
                'value',
                'date',
                'currency',
            )

    value = ValueSerializer(source='*')
    type = serializers.CharField(source='type.code')

    class Meta(activity_serializers.BudgetSerializer.Meta):
        fields = (
            'type',
            'period_start',
            'period_end',
            'value',
        )


class ActivityDateSerializer(XMLMetaMixin, activity_serializers.ActivityDateSerializer):
    xml_meta = {'attributes': ('type', 'iso_date')}

    type = serializers.CharField(source='type.code')
    iso_date = serializers.DateTimeField()

    class Meta(activity_serializers.ActivityDateSerializer.Meta):
        fields = ('iso_date', 'type')


class ActivityAggregationSerializer(DynamicFieldsSerializer):
    budget_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    budget_currency = serializers.CharField()
    disbursement_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    disbursement_currency = serializers.CharField()
    incoming_funds_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    incoming_funds_currency = serializers.CharField()
    commitment_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    commitment_currency = serializers.CharField()
    expenditure_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    expenditure_currency = serializers.CharField()


class ReportingOrganisationSerializer(XMLMetaMixin, activity_serializers.ReportingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'secondary_reporter')}

    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source="normalized_ref")
    type = serializers.CharField(source='type.code')
    secondary_reporter = serializers.BooleanField()
    narratives = NarrativeSerializer(many=True)

    class Meta(activity_serializers.ReportingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narratives',
        )

class ParticipatingOrganisationSerializer(XMLMetaMixin, activity_serializers.ParticipatingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'role',)}

    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = serializers.CharField(source='type.code')
    role = serializers.CharField(source='role.code')
    narratives = NarrativeSerializer(many=True)

    class Meta(activity_serializers.ParticipatingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'role',
            'narratives',
        )

class ActivityPolicyMarkerSerializer(XMLMetaMixin, activity_serializers.ActivityPolicyMarkerSerializer):
    xml_meta = {'attributes': ('code', 'vocabulary', 'significance',)}

    code = CodelistSerializer()
    vocabulary = VocabularySerializer()
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta(activity_serializers.ActivityPolicyMarkerSerializer.Meta):
        fields = (
            'narratives',
            'vocabulary',
            'significance',
            'code',
        )


# TODO: change to NarrativeContainer
class TitleSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

    class Meta(activity_serializers.TitleSerializer.Meta):
        fields = ('narratives',)

class DescriptionSerializer(XMLMetaMixin, activity_serializers.DescriptionSerializer):
    xml_meta = {'attributes': ('type',)}

    type = serializers.CharField(source='type.code')
    type = serializers.CharField(source='type.code')
    narratives = NarrativeSerializer(many=True)

    class Meta(activity_serializers.DescriptionSerializer.Meta):
        fields = (
            'type',
            'narratives'
        )

class RelatedActivityTypeSerializer(XMLMetaMixin, activity_serializers.RelatedActivityTypeSerializer):
    xml_meta = {'attributes': ('only', 'code')}

    class Meta(activity_serializers.RelatedActivityTypeSerializer.Meta):
        fields = (
            'code',
        )

class RelatedActivitySerializer(XMLMetaMixin, activity_serializers.RelatedActivitySerializer):
    xml_meta = {'attributes': ('ref_activity', 'type')}
    
    ref_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    type = RelatedActivityTypeSerializer()

    class Meta(activity_serializers.RelatedActivitySerializer.Meta):
        fields = (
            'ref_activity',
            'ref',
            'type',
        )

class ActivitySectorSerializer(XMLMetaMixin, activity_serializers.ActivitySectorSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'sector',), 'rename': {'sector': 'code'}}

    sector = SectorSerializer(fields=('url', 'code'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()

    class Meta(activity_serializers.ActivitySectorSerializer.Meta):
        fields = (
            'sector',
            'percentage',
            'vocabulary',
        )


class ActivityRecipientRegionSerializer(XMLMetaMixin, activity_serializers.ActivityRecipientRegionSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'region',), 'rename': {'region': 'code'}}

    region = RegionSerializer(
        fields=('url', 'code')
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()

    class Meta(activity_serializers.ActivityRecipientRegionSerializer.Meta):
        fields = (
            'region',
            'percentage',
            'vocabulary',
        )

class RecipientCountrySerializer(XMLMetaMixin, activity_serializers.RecipientCountrySerializer):
    xml_meta = {'attributes': ('percentage', 'country'), 'rename': {'country': 'code'}}

    country = CountrySerializer(fields=('url', 'code'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    # vocabulary = VocabularySerializer()

    class Meta(activity_serializers.RecipientCountrySerializer.Meta):
        fields = (
            'country',
            'percentage',
        )


class ResultTypeSerializer(XMLMetaMixin, activity_serializers.ResultTypeSerializer):
    xml_meta = {'only': 'code'}

    class Meta(activity_serializers.ResultTypeSerializer.Meta):
        fields = (
            'code',
        )

class ResultDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta(activity_serializers.ResultDescriptionSerializer.Meta):
        fields = (
            'narratives',
        )

class ResultTitleSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta(activity_serializers.ResultTitleSerializer.Meta):
        fields = (
            'narratives',
        )


class ResultIndicatorPeriodTargetSerializer(XMLMetaMixin, activity_serializers.ResultIndicatorPeriodTargetSerializer):
    xml_meta = {'attributes': ('value',)}

    # TO DO 2.02 : location = 
    # TO DO 2.02 : dimension = 
    value = serializers.CharField(source='target')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodtargetcomment")

class ResultIndicatorPeriodActualSerializer(XMLMetaMixin, activity_serializers.ResultIndicatorPeriodActualSerializer):
    xml_meta = {'attributes': ('value',)}

    # TO DO 2.02 : location = 
    # TO DO 2.02 : dimension = 
    value = serializers.CharField(source='actual')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodactualcomment")

class ResultIndicatorPeriodSerializer(serializers.ModelSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*")
    actual = ResultIndicatorPeriodActualSerializer(source="*")

    class Meta(activity_serializers.ResultIndicatorPeriodSerializer.Meta):
        fields = (
            'period_start',
            'period_end',
            'target',
            'actual',
        )

class ResultIndicatorBaselineSerializer(XMLMetaMixin, activity_serializers.ResultIndicatorBaselineSerializer):
    xml_meta = {'attributes': ('year', 'value',)}

    year = serializers.CharField(source='baseline_year')
    value = serializers.CharField(source='baseline_value')
    comment = NarrativeContainerSerializer(source="resultindicatorbaselinecomment")

class ResultIndicatorSerializer(serializers.ModelSerializer):
    title = NarrativeContainerSerializer(source="resultindicatortitle")
    description = NarrativeContainerSerializer(source="resultindicatordescription")
    #  TO DO 2.02 reference = ? 
    baseline = ResultIndicatorBaselineSerializer(source="*")
    period = ResultIndicatorPeriodSerializer(source='resultindicatorperiod_set', many=True)
    measure = CodelistSerializer()

    class Meta(activity_serializers.ResultIndicatorSerializer.Meta):
        fields = (
            'title',
            'description',
            'baseline',
            'period',
            'measure',
            'ascending'
        )

class ResultSerializer(XMLMetaMixin, activity_serializers.ResultSerializer):
    xml_meta = {'attributes': ('type', 'aggregation_status',)}

    type = serializers.CharField(source='type.code')
    title = NarrativeContainerSerializer(source="resulttitle")
    description = NarrativeContainerSerializer(source="resultdescription")
    indicator = ResultIndicatorSerializer(source='resultindicator_set', many=True)

    class Meta(activity_serializers.ResultSerializer.Meta):
        fields = (
            'title',
            'description',
            'indicator',
            'type',
            'aggregation_status',
        )

class LocationSerializer(XMLMetaMixin, activity_serializers.LocationSerializer):
    xml_meta = {'attributes': ('ref',)}

    class LocationIdSerializer(XMLMetaMixin, activity_serializers.LocationSerializer.LocationIdSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary',)}

        vocabulary = VocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')

    class PointSerializer(XMLMetaMixin, activity_serializers.LocationSerializer.PointSerializer):
        xml_meta = {'attributes': ('srs_name',)}

        pos = PointField(source='point_pos')
        srs_name = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(XMLMetaMixin, activity_serializers.LocationSerializer.AdministrativeSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary', 'level')}

        code = serializers.CharField()
        vocabulary = VocabularySerializer()

        class Meta(activity_serializers.LocationSerializer.AdministrativeSerializer.Meta):
            fields = (
                'code',
                'vocabulary',
                'level',
            )

    location_reach = CodelistSerializer()
    location_id = LocationIdSerializer(source='*')
    name = NarrativeContainerSerializer(many=True, source="locationname_set")
    description = NarrativeContainerSerializer(many=True, source="locationdescription_set")
    activity_description = NarrativeContainerSerializer(many=True, source="locationactivitydescription_set")
    administrative = AdministrativeSerializer(many=True, source="locationadministrative_set")
    point = PointSerializer(source="*")
    exactness = CodelistSerializer()
    location_class = CodelistSerializer()
    feature_designation = CodelistCategorySerializer()
    
    class Meta(activity_serializers.LocationSerializer.Meta):
        fields = (
            'ref',
            'location_reach',
            'location_id',
            'name',
            'description',
            'activity_description',
            'administrative',
            'point',
            'exactness',
            'location_class',
            'feature_designation',
        )











class TransactionProviderSerializer(XMLMetaMixin, transaction_serializers.TransactionProviderSerializer):
    xml_meta = {'attributes': ('ref', 'provider_activity_id',)}

    ref = serializers.CharField(source="normalized_ref")
    narrative = NarrativeSerializer(many=True, source='narratives')
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    provider_activity_id = serializers.CharField(source="provider_activity_ref")

    class Meta(transaction_serializers.TransactionDescriptionSerializer.Meta):
        fields = (
            'ref',
            'provider_activity_id',
            'narrative'
        )


class TransactionReceiverSerializer(XMLMetaMixin, transaction_serializers.TransactionReceiverSerializer):
    xml_meta = {'attributes': ('ref', 'receiver_activity_id',)}

    ref = serializers.CharField(source="normalized_ref")
    narrative = NarrativeSerializer(many=True, source='narratives')
    receiver_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    receiver_activity_id = serializers.CharField(source="receiver_activity_ref")

    class Meta(transaction_serializers.TransactionReceiverSerializer.Meta):
        fields = (
            'ref',
            'receiver_activity_id',
            'narrative'
        )


class TransactionDescriptionSerializer(XMLMetaMixin, transaction_serializers.TransactionDescriptionSerializer):
    narratives = NarrativeSerializer(many=True)


class TransactionSerializer(XMLMetaMixin, transaction_serializers.TransactionSerializer):
    class ValueSerializer(XMLMetaMixin, serializers.Serializer):
        xml_meta = {'attributes': ('currency', 'value_date',)}

        currency = serializers.CharField(source='currency.code')
        value_date = serializers.CharField()
        text = serializers.DecimalField(
            source='value',
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
        )

        class Meta(activity_serializers.BudgetSerializer.ValueSerializer.Meta):
            fields = (
                'text',
                'value_date',
                'currency',
            )

    class TransactionDateSerializer(XMLMetaMixin, serializers.Serializer):
        xml_meta = {'attributes': ('iso_date',)}

        iso_date = serializers.CharField(source='transaction_date')

    xml_meta = {'attributes': ('ref', 'type',)}

    url = serializers.HyperlinkedIdentityField(
        view_name='transactions:transaction-detail',
        lookup_field='pk')

    transaction_type = serializers.CharField(source='transaction_type.code')
    description = TransactionDescriptionSerializer()
    provider_org = TransactionProviderSerializer(source='provider_organisation')
    receiver_org = TransactionReceiverSerializer(source='receiver_organisation')
    flow_type = serializers.CharField(source='flow_type.code')
    finance_type = serializers.CharField(source='finance_type.code')
    aid_type = serializers.CharField(source='aid_type.code')
    tied_status = CodelistSerializer()
    currency = CodelistSerializer()

    value = ValueSerializer(source='*')
    transaction_date = TransactionDateSerializer(source='*')

    class Meta(transaction_serializers.TransactionSerializer.Meta):
        fields = (
            'ref',
            'transaction_type',
            'transaction_date',
            'value',
            'description',
            'provider_org',
            'receiver_org',
            'disbursement_channel',
            # 'sector',
            # 'recipient_country',
            # 'recipient_region',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
        )













class ActivityXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivitySerializer):
    xml_meta = {'attributes': ('default_currency', 'last_updated_datetime', 'linked_data_uri', 'hierarchy', 'xml_lang')}

    iati_identifier = serializers.CharField()
    reporting_org = ReportingOrganisationSerializer(
        source='reporting_organisations',
        many=True,)
    title = TitleSerializer()
    description = DescriptionSerializer(
        many=True, read_only=True, source='description_set')
    participating_org = ParticipatingOrganisationSerializer(
        source='participating_organisations',
        many=True,)

    # TO DO ; add other-identifier serializer
    # other_identifier = serializers.OtherIdentifierSerializer(many=True,source="?")

    activity_status = CodelistSerializer()
    activity_date = ActivityDateSerializer(
        many=True,
        source='activitydate_set')

    # TO DO ; add contact-info serializer
    # note; contact info has a sequence we should use in the ContactInfoSerializer!
    # contact_info = serializers.ContactInfoSerializer(many=True,source="?")

    activity_scope = CodelistSerializer(source='scope')
    recipient_country = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set')
    recipient_region = ActivityRecipientRegionSerializer(
        many=True,
        source='activityrecipientregion_set')
    location = LocationSerializer(many=True, source='location_set')
    sector = ActivitySectorSerializer(
        many=True,
        source='activitysector_set')

    # TO DO ; add country-budget-items serializer
    # country_budget_items = serializers.CountryBudgetItemsSerializer(many=True,source="?")

    # TO DO ; add humanitarian-scope serializer
    # humanitarian_scope = serializers.HumanitarianScopeSerializer(many=True,source="?")

    policy_marker = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = serializers.CharField(source='collaboration_type.code')
    default_flow_type = serializers.CharField(source='default_flow_type.code')
    default_finance_type = serializers.CharField(source='default_finance_type.code')
    default_aid_type = serializers.CharField(source='default_aid_type.code')
    default_tied_status = CodelistSerializer()

    budget = BudgetSerializer(many=True, source='budget_set')

    # TO DO ; add planned-disbursement serializer
    # note; planned-disbursement has a sequence in PlannedDisbursementSerializer
    # planned_disbursement = serializers.PlannedDisbursementSerializer(many=True,source="?")

    capital_spend = CapitalSpendSerializer(source='*')
    transaction = TransactionSerializer(many=True, source='transaction_set')
    # TO DO ; hook up with the serializer instead of HyperlinkedIdentityField
    # to be able to serialize it in XML
    # 
    # transaction = TransactionSerializer(
    #     many=True,
    #     source='transaction_set')
    document_link = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    related_activity = RelatedActivitySerializer(
        many=True, 
        source='relatedactivity_set')

    # TO DO ; add legacy-data serializer? note: we dont parse legacy data atm.
    # legacy_data = LegacyDataSerializer(many=True, source="?")

    # TO DO ; add conditions serializer
    # conditions = serializers.ConditionsSerializer(many=True,source="?")

    result = ResultSerializer(many=True, source="result_set")
    
    # TO DO ; add crs-add serializer
    # note; crs-add has a sequence in CrsAddSerializer
    # crs_add = serializers.CrsAddSerializer(many=True, source="?")

    # TO DO ; add fss serializer
    # fss = serializers.FssSerializer(many=True, source="?") 
    
    # activity attributes
    last_updated_datetime = serializers.DateTimeField()
    xml_lang = serializers.CharField(source='default_lang')
    default_currency = CodelistSerializer()
    # TO DO 2.02; humanitarian = serializers.BooleanField()

    # other added data
    activity_aggregation = ActivityAggregationSerializer()
    child_aggregation = ActivityAggregationSerializer()
    activity_plus_child_aggregation = ActivityAggregationSerializer()

    class Meta(activity_serializers.ActivitySerializer.Meta):
        fields = (
            'iati_identifier',
            'reporting_org',
            'title',
            'description',
            'participating_org',
            # 'other_identifier',
            'activity_status',
            'activity_date',
            # 'contact_info',
            'activity_scope',
            'recipient_country',
            'recipient_region',
            'location',
            'sector',
            # 'country_budget_items',
            # 'humanitarian_scope',
            'policy_marker',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            # 'planned_disbursement',
            'budget',
            'capital_spend',
            'transaction',
            'document_link',
            'related_activity',
            # 'legacy_data',
            # 'conditions',
            'result',
            # 'crs_add',
            # 'fss',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            # 'humanitarian',
            'hierarchy',
            'linked_data_uri',
            # 'xml_source_ref',
        )

