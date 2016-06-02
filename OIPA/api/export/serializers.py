from rest_framework import serializers
from api.generics.fields import PointIATIField
from api.generics.serializers import XMLMetaMixin
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import SkipNullMixin
import api.activity.serializers as activity_serializers
import api.transaction.serializers as transaction_serializers


class ValueSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    xml_meta = {'attributes': ('currency', 'value_date')}

    currency = serializers.CharField(source='currency.code')
    value_date = serializers.CharField()
    text = serializers.DecimalField(
            source='value',
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
            )

    class Meta():
        fields = (
                'text',
                'value_date',
                'currency',
                )


class IsoDateSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    xml_meta = {'attributes': ('iso_date',)}

    iso_date = serializers.CharField(source='*')

class CodelistSerializer(XMLMetaMixin, SkipNullMixin, DynamicFieldsSerializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField()

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

# TODO: separate this
class NarrativeXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.NarrativeSerializer):
    xml_meta = {'attributes': ('xml_lang',)}

    xml_lang = serializers.CharField(source='language.code')

    class Meta(activity_serializers.NarrativeSerializer.Meta):
        fields = (
            'text',
            'xml_lang',
        )

class NarrativeContainerXMLSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    narrative = NarrativeXMLSerializer(many=True, source='narratives')


class DocumentCategorySerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DocumentCategorySerializer):
    xml_meta = {'attributes': ('code',)}

    class Meta(activity_serializers.DocumentCategorySerializer.Meta):
        fields = ('code',)

class DocumentLinkSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DocumentLinkSerializer):
    xml_meta = {'attributes': ('url', 'format',)}

    format = serializers.CharField(source='file_format.code')
    category = DocumentCategorySerializer(many=True, source='categories')
    title = NarrativeContainerXMLSerializer(source="documentlinktitle_set", many=True)

    class Meta(activity_serializers.DocumentLinkSerializer.Meta):
        fields = (
            'url',
            'format',
            'title',
            'category',
        )


class CapitalSpendSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.CapitalSpendSerializer):
    xml_meta = {'attributes': ('percentage',)}


class BudgetSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.BudgetSerializer):
    xml_meta = {'attributes': ('type',)}

    value = ValueSerializer(source='*')
    type = serializers.CharField(source='type.code')
    status = serializers.CharField(source='status.code')

    period_start = IsoDateSerializer()
    period_end = IsoDateSerializer()

    class Meta(activity_serializers.BudgetSerializer.Meta):
        fields = (
            'type',
            'status',
            'period_start',
            'period_end',
            'value',
        )

class PlannedDisbursementSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.PlannedDisbursementSerializer):
    xml_meta = {'attributes': ('type',)}

    value = ValueSerializer(source='*')
    type = serializers.CharField(source='type.code')

    period_start = IsoDateSerializer()
    period_end = IsoDateSerializer()

    class Meta(activity_serializers.PlannedDisbursementSerializer.Meta):
        fields = (
            'type',
            'period_start',
            'period_end',
            'value',
        )

class ActivityDateSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivityDateSerializer):
    xml_meta = {'attributes': ('type', 'iso_date')}

    type = serializers.CharField(source='type.code')


class ReportingOrganisationSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ReportingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'secondary_reporter')}

    type = serializers.CharField(source='type.code')
    narrative = NarrativeXMLSerializer(many=True, source='narratives')

    class Meta(activity_serializers.ReportingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narrative',
        )

class ParticipatingOrganisationSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ParticipatingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'role', 'activity_id')}

    type = serializers.CharField(source='type.code')
    role = serializers.CharField(source='role.code')
    narrative = NarrativeXMLSerializer(many=True, source='narratives')
    activity_id = serializers.CharField(source='org_activity_id')

    class Meta(activity_serializers.ParticipatingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'role',
            'activity_id',
            'narrative',
        )

class ActivityPolicyMarkerSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivityPolicyMarkerSerializer):
    xml_meta = {'attributes': ('code', 'vocabulary', 'significance',)}

    code = serializers.CharField(source='code.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()
    significance = serializers.CharField(source='significance.code')
    narrative = NarrativeXMLSerializer(many=True, source='narratives')

    class Meta(activity_serializers.ActivityPolicyMarkerSerializer.Meta):
        fields = (
            'narrative',
            'vocabulary',
            'vocabulary_uri',
            'significance',
            'code',
        )


class DescriptionSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DescriptionSerializer):
    xml_meta = {'attributes': ('type',)}

    type = serializers.CharField(source='type.code')
    narrative = NarrativeXMLSerializer(many=True, source='narratives')

    class Meta(activity_serializers.DescriptionSerializer.Meta):
        fields = (
            'type',
            'narrative'
        )

class RelatedActivitySerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.RelatedActivitySerializer):
    xml_meta = {'attributes': ('ref', 'type')}
    
    type = serializers.CharField(source='type.code')

    class Meta(activity_serializers.RelatedActivitySerializer.Meta):
        fields = (
            'ref',
            'type',
        )

class ActivitySectorSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivitySectorSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'code',)}

    code = serializers.CharField(source='sector.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()

    class Meta(activity_serializers.ActivitySectorSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

class ActivitySectorSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivitySectorSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'code',)}

    code = serializers.CharField(source='sector.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()

    class Meta(activity_serializers.ActivitySectorSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

class ActivityRecipientRegionSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivityRecipientRegionSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'vocabulary_uri', 'code',)}

    code = serializers.CharField(source='region.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()

    class Meta(activity_serializers.ActivityRecipientRegionSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )


class HumanitarianScopeSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.HumanitarianScopeSerializer):
    xml_meta = {'attributes': ('type', 'vocabulary', 'vocabulary_uri', 'code',)}

    type = serializers.CharField(source='type.code')
    code = serializers.CharField(source='code.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()


class RecipientCountrySerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.RecipientCountrySerializer):
    xml_meta = {'attributes': ('percentage', 'code')}

    code = serializers.CharField(source='country.code')
    # vocabulary = serializers.CharField(source='vocabulary.code')

    class Meta(activity_serializers.RecipientCountrySerializer.Meta):
        fields = (
            'code',
            'percentage',
        )


class ResultIndicatorPeriodTargetSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodTargetSerializer):
    xml_meta = {'attributes': ('value',)}

    comment = NarrativeContainerXMLSerializer(source="resultindicatorperiodtargetcomment")

class ResultIndicatorPeriodActualSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodActualSerializer):
    xml_meta = {'attributes': ('value',)}

    comment = NarrativeContainerXMLSerializer(source="resultindicatorperiodactualcomment")

class ResultIndicatorPeriodXMLSerializer(SkipNullMixin, activity_serializers.ResultIndicatorPeriodSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*")
    actual = ResultIndicatorPeriodActualSerializer(source="*")

    period_start = IsoDateSerializer()
    period_end = IsoDateSerializer()

class ResultIndicatorBaselineXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorBaselineSerializer):
    xml_meta = {'attributes': ('year', 'value',)}

    comment = NarrativeContainerXMLSerializer(source="resultindicatorbaselinecomment")

class ResultIndicatorXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorSerializer):
    xml_meta = {'attributes': ('measure', 'ascending',)}

    title = NarrativeContainerXMLSerializer(source="resultindicatortitle")
    description = NarrativeContainerXMLSerializer(source="resultindicatordescription")
    baseline = ResultIndicatorBaselineXMLSerializer(source="*")
    period = ResultIndicatorPeriodXMLSerializer(source='resultindicatorperiod_set', many=True)
    measure = serializers.CharField(source='measure.code')

class ResultXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultSerializer):
    xml_meta = {'attributes': ('type', 'aggregation_status',)}

    type = serializers.CharField(source='type.code')
    title = NarrativeContainerXMLSerializer(source="resulttitle")
    description = NarrativeContainerXMLSerializer(source="resultdescription")
    indicator = ResultIndicatorXMLSerializer(source='resultindicator_set', many=True)


class LocationSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer):
    xml_meta = {'attributes': ('ref',)}

    class LocationIdSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.LocationIdSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary',)}

        vocabulary = serializers.CharField(
            source='location_id_vocabulary.code')

    class PointSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.PointSerializer):
        xml_meta = {'attributes': ('srsName',)}

        
        pos = PointIATIField(source='point_pos')
#         srsName = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.AdministrativeSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary', 'level')}

        vocabulary = serializers.CharField(source='vocabulary.code')

    location_id = LocationIdSerializer(source='*')
    activity_description = NarrativeContainerXMLSerializer(many=True, source="locationactivitydescription_set")
    administrative = AdministrativeSerializer(many=True, source="locationadministrative_set")
    point = PointSerializer(source="*")
    exactness = CodelistSerializer()
    # class Meta(transaction_serializers.LocationSerializer.Meta):
    #     pass

class TransactionProviderSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionProviderSerializer):
    xml_meta = {'attributes': ('ref', 'provider_activity_id',)}

    narrative = NarrativeXMLSerializer(many=True, source='narratives')

    class Meta(transaction_serializers.TransactionProviderSerializer.Meta):
        fields = (
            'ref',
            'provider_activity_id',
            'narrative'
        )

class TransactionReceiverSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionReceiverSerializer):
    xml_meta = {'attributes': ('ref', 'receiver_activity_id',)}

    narrative = NarrativeXMLSerializer(many=True, source='narratives')

    class Meta(transaction_serializers.TransactionReceiverSerializer.Meta):
        fields = (
            'ref',
            'receiver_activity_id',
            'narrative'
        )


class TransactionSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionSerializer):
    xml_meta = {'attributes': ('ref', 'type',)}

    transaction_type = CodelistSerializer()
    description = NarrativeContainerXMLSerializer()
    provider_org = TransactionProviderSerializer(source='provider_organisation')
    receiver_org = TransactionReceiverSerializer(source='receiver_organisation')
    flow_type = CodelistSerializer()
    finance_type = CodelistSerializer()
    aid_type = CodelistSerializer()
    tied_status = CodelistSerializer()
    currency = CodelistSerializer()

    value = ValueSerializer(source='*')
    transaction_date = IsoDateSerializer()
    disbursement_channel = CodelistSerializer()

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
            # recipient_country',
            # 'recipient_region',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
        )

class ActivityXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivitySerializer):
    xml_meta = {'attributes': ('default_currency', 'last_updated_datetime', 'humanitarian', 'linked_data_uri', 'hierarchy', 'xml_lang')}

    reporting_org = ReportingOrganisationSerializer(
        source='reporting_organisations',
        many=True,)
    title = NarrativeContainerXMLSerializer()
    description = DescriptionSerializer(
        many=True, read_only=True, source='description_set')
    participating_org = ParticipatingOrganisationSerializer(
        source='participating_organisations',
        many=True,)

    activity_status = CodelistSerializer()
    activity_date = ActivityDateSerializer(
        many=True,
        source='activitydate_set')

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

    humanitarian_scope = HumanitarianScopeSerializer(many=True,source="?")

    policy_marker = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budget = BudgetSerializer(many=True, source='budget_set')
    planned_disbursement = PlannedDisbursementSerializer(many=True, source='planned_disbursement_set')

    capital_spend = CapitalSpendSerializer()
    transaction = TransactionSerializer(
        many=True,
        source='transaction_set')

    document_link = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    related_activity = RelatedActivitySerializer(
        many=True, 
        source='relatedactivity_set')

    result = ResultXMLSerializer(many=True, source="result_set")

    humanitarian = serializers.BooleanField()
    
    default_currency = serializers.CharField(source='default_currency.code')

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
            'planned_disbursement',
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
            'humanitarian',
            'hierarchy',
            'linked_data_uri',
            # 'xml_source_ref',
        )

