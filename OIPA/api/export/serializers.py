from rest_framework import serializers
from api.generics.serializers import XMLMetaMixin
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import SkipNullMixin
import api.activity.serializers as activity_serializers
import api.transaction.serializers as transaction_serializers


class IsoDateSerializer(XMLMetaMixin, serializers.Serializer):
    xml_meta = {'attributes': ('iso_date',)}

    iso_date = serializers.CharField(source='*')

class CodelistSerializer(XMLMetaMixin, DynamicFieldsSerializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField()

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

# TODO: separate this
class NarrativeSerializer(XMLMetaMixin, activity_serializers.NarrativeSerializer):
    xml_meta = {'attributes': ('xml_lang',)}

    xml_lang = serializers.CharField(source='language.code')

    class Meta(activity_serializers.NarrativeSerializer.Meta):
        fields = ('xml_lang', 'text',)

class NarrativeContainerSerializer(serializers.Serializer):
    narrative = NarrativeSerializer(many=True, source='narratives')


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

    class Meta(activity_serializers.CapitalSpendSerializer.Meta):
        fields = ('percentage',)


class BudgetSerializer(XMLMetaMixin, activity_serializers.BudgetSerializer):
    xml_meta = {'attributes': ('type',)}

    class ValueSerializer(XMLMetaMixin, serializers.Serializer):
        xml_meta = {'attributes': ('currency', 'value_date')}

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

    value = ValueSerializer(source='*')
    type = serializers.CharField(source='type.code')

    period_start = IsoDateSerializer()
    period_end = IsoDateSerializer()

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


class ReportingOrganisationSerializer(XMLMetaMixin, activity_serializers.ReportingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'secondary_reporter')}

    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source="normalized_ref")
    type = serializers.CharField(source='type.code')
    secondary_reporter = serializers.BooleanField()
    narrative = NarrativeSerializer(many=True, source='narratives')

    class Meta(activity_serializers.ReportingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narrative',
        )

class ParticipatingOrganisationSerializer(XMLMetaMixin, activity_serializers.ParticipatingOrganisationSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'role',)}

    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = serializers.CharField(source='type.code')
    role = serializers.CharField(source='role.code')
    narrative = NarrativeSerializer(many=True, source='narratives')

    class Meta(activity_serializers.ParticipatingOrganisationSerializer.Meta):
        fields = (
            'ref',
            'type',
            'role',
            'narrative',
        )

class ActivityPolicyMarkerSerializer(XMLMetaMixin, activity_serializers.ActivityPolicyMarkerSerializer):
    xml_meta = {'attributes': ('code', 'vocabulary', 'significance',)}

    code = serializers.CharField(source='code.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    significance = CodelistSerializer()
    narrative = NarrativeSerializer(many=True, source='narratives')

    class Meta(activity_serializers.ActivityPolicyMarkerSerializer.Meta):
        fields = (
            'narrative',
            'vocabulary',
            'significance',
            'code',
        )


class DescriptionSerializer(XMLMetaMixin, activity_serializers.DescriptionSerializer):
    xml_meta = {'attributes': ('type',)}

    type = serializers.CharField(source='type.code')
    narrative = NarrativeSerializer(many=True, source='narratives')

    class Meta(activity_serializers.DescriptionSerializer.Meta):
        fields = (
            'type',
            'narrative'
        )

class RelatedActivitySerializer(XMLMetaMixin, activity_serializers.RelatedActivitySerializer):
    xml_meta = {'attributes': ('ref', 'type')}
    
    ref = serializers.CharField(source='ref_activity')
    type = serializers.CharField(source='type.code')

    class Meta(activity_serializers.RelatedActivitySerializer.Meta):
        fields = (
            'ref',
            'ref',
            'type',
        )

class ActivitySectorSerializer(XMLMetaMixin, activity_serializers.ActivitySectorSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'code',)}

    code = serializers.CharField(source='sector.code')
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = serializers.CharField(source='vocabulary.code')

    class Meta(activity_serializers.ActivitySectorSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
        )


class ActivityRecipientRegionSerializer(XMLMetaMixin, activity_serializers.ActivityRecipientRegionSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'code',)}

    code = serializers.CharField(source='region.code')
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = serializers.CharField(source='vocabulary.code')

    class Meta(activity_serializers.ActivityRecipientRegionSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
        )

class RecipientCountrySerializer(XMLMetaMixin, activity_serializers.RecipientCountrySerializer):
    xml_meta = {'attributes': ('percentage', 'code')}

    code = serializers.CharField(source='country.code')
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    # vocabulary = serializers.CharField(source='vocabulary.code')

    class Meta(activity_serializers.RecipientCountrySerializer.Meta):
        fields = (
            'code',
            'percentage',
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

    period_start = IsoDateSerializer()
    period_end = IsoDateSerializer()

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

        vocabulary = serializers.CharField(
            source='location_id_vocabulary.code')
        code = serializers.CharField(source='location_id_code')

    class PointSerializer(XMLMetaMixin, activity_serializers.LocationSerializer.PointSerializer):
        xml_meta = {'attributes': ('srsName',)}

        srsName = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(XMLMetaMixin, activity_serializers.LocationSerializer.AdministrativeSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary', 'level')}

        code = serializers.CharField()
        vocabulary = serializers.CharField(source='vocabulary.code')

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


class TransactionSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionSerializer):
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

    xml_meta = {'attributes': ('ref', 'type',)}

    url = serializers.HyperlinkedIdentityField(
        view_name='transactions:transaction-detail',
        lookup_field='pk')

    transaction_type = CodelistSerializer()
    description = NarrativeContainerSerializer()
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
            # 'recipient_country',
            # 'recipient_region',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
        )













class ActivityXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivitySerializer):
    xml_meta = {'attributes': ('default_currency', 'last_updated_datetime', 'linked_data_uri', 'hierarchy', 'xml_lang')}

    reporting_org = ReportingOrganisationSerializer(
        source='reporting_organisations',
        many=True,)
    title = NarrativeContainerSerializer()
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

    policy_marker = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budget = BudgetSerializer(many=True, source='budget_set')

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

    result = ResultSerializer(many=True, source="result_set")
    
    default_currency = CodelistSerializer()

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

