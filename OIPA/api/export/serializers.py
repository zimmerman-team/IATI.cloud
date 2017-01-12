from rest_framework import serializers
from api.generics.fields import PointIATIField
from api.generics.serializers import XMLMetaMixin
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import SkipNullMixin
import api.activity.serializers as activity_serializers
import api.transaction.serializers as transaction_serializers

from iati import models as iati_models

class BoolToNumField(serializers.Field):
    """
    represent True and False as "1" and "0"
    """
    def to_representation(self, val):
        if val:
            return "1"
        else:
            return "0"

    # def to_internal_value(self, data):
    #     data = data.strip('rgb(').rstrip(')')
    #     red, green, blue = [int(col) for col in data.split(',')]
    #     return Color(red, green, blue)

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


class DocumentLinkCategorySerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DocumentLinkCategorySerializer):
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField(source='category.code')

    class Meta(activity_serializers.DocumentLinkCategorySerializer.Meta):
        fields = ('code',)

class DocumentLinkLanguageSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DocumentLinkLanguageSerializer):
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField(source='language.code')

    class Meta(activity_serializers.DocumentLinkLanguageSerializer.Meta):
        fields = ('code',)


class DocumentLinkXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.DocumentLinkSerializer):
    xml_meta = {'attributes': ('url', 'format',)}

    class DocumentDateSerializer(serializers.Serializer):
        # CharField because we want to let the validators do the parsing
        iso_date = serializers.CharField()

    format = serializers.CharField(source='file_format.code')

    category = DocumentLinkCategorySerializer(many=True, source='documentlinkcategory_set')
    language = DocumentLinkLanguageSerializer(many=True, source='documentlinklanguage_set')

    title = NarrativeContainerXMLSerializer(source='documentlinktitle')
    document_date = IsoDateSerializer(source="iso_date")

    class Meta(activity_serializers.DocumentLinkSerializer.Meta):
        fields = (
            'url',
            'format',
            'title',
            'category',
            'language',
            'document_date',
        )


class CapitalSpendSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.CapitalSpendSerializer):
    xml_meta = {'attributes': ('percentage',)}


class LegacyDataXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LegacyDataSerializer):
    xml_meta = {'attributes': ('name', 'value', 'iati_equivalent', )}

    name = serializers.CharField()
    value = serializers.CharField()
    iati_equivalent = serializers.CharField()


    class Meta(activity_serializers.LegacyDataSerializer.Meta):
        fields = (
            'name',
            'value',
            'iati_equivalent',
        )

class BudgetSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.BudgetSerializer):
    xml_meta = {'attributes': ('type', 'status')}

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
    secondary_reporter = BoolToNumField()

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

class OtherIdentifierXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.OtherIdentifierSerializer):
    xml_meta = {'attributes': ('ref', 'type',)}

    class OwnerOrgSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
        xml_meta = {'attributes': ('ref',)}

        ref = serializers.CharField(source='owner_ref')
        narrative = NarrativeXMLSerializer(many=True, source='narratives')

    ref = serializers.CharField(source="identifier")
    type = serializers.CharField(source='type.code')

    owner_org = OwnerOrgSerializer(source="*")

    class Meta(activity_serializers.OtherIdentifierSerializer.Meta):
        fields = (
            # 'id',
            'ref',
            'type',
            'owner_org'
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
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'vocabulary_uri', 'code',)}

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


class ActivityRecipientRegionXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ActivityRecipientRegionSerializer):
    xml_meta = {'attributes': ('percentage', 'vocabulary', 'vocabulary_uri', 'code',)}

    code = serializers.CharField(source='region.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()
    # vocabulary_uri = serializers.CharField()

    class Meta(activity_serializers.ActivityRecipientRegionSerializer.Meta):
        fields = (
            'code',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )


class HumanitarianScopeXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.HumanitarianScopeSerializer):
    xml_meta = {'attributes': ('type', 'vocabulary', 'code',)}

    type = serializers.CharField(source='type.code')
    code = serializers.CharField()
    vocabulary = serializers.CharField(source='vocabulary.code')
    # vocabulary_uri = serializers.URLField()


    class Meta(activity_serializers.HumanitarianScopeSerializer.Meta):
        fields = (
            'type',
            'vocabulary',
            # 'vocabulary_uri',
            'code',
        )


class RecipientCountrySerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.RecipientCountrySerializer):
    xml_meta = {'attributes': ('percentage', 'code')}

    code = serializers.CharField(source='country.code')
    # vocabulary = serializers.CharField(source='vocabulary.code')

    class Meta(activity_serializers.RecipientCountrySerializer.Meta):
        fields = (
            'code',
            'percentage',
        )


class ResultIndicatorPeriodActualLocationXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodActualLocationSerializer):
    xml_meta = {'attributes': ('ref',)}
class ResultIndicatorPeriodTargetLocationXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodTargetLocationSerializer):
    xml_meta = {'attributes': ('ref',)}


class ResultIndicatorPeriodActualDimensionXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodActualDimensionSerializer):
    xml_meta = {'attributes': ('name', 'value')}

class ResultIndicatorPeriodTargetDimensionXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodTargetDimensionSerializer):
    xml_meta = {'attributes': ('name', 'value')}


class ResultIndicatorPeriodTargetSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodTargetSerializer):
    xml_meta = {'attributes': ('value',)}

    location = ResultIndicatorPeriodTargetLocationXMLSerializer(many=True, source="resultindicatorperiodtargetlocation_set")
    dimension = ResultIndicatorPeriodTargetDimensionXMLSerializer(many=True, source="resultindicatorperiodtargetdimension_set")
    comment = NarrativeContainerXMLSerializer(source="resultindicatorperiodtargetcomment")


class ResultIndicatorPeriodActualSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ResultIndicatorPeriodActualSerializer):
    xml_meta = {'attributes': ('value',)}

    location = ResultIndicatorPeriodActualLocationXMLSerializer(many=True, source="resultindicatorperiodactuallocation_set")
    dimension = ResultIndicatorPeriodActualDimensionXMLSerializer(many=True, source="resultindicatorperiodactualdimension_set")
    comment = NarrativeContainerXMLSerializer(source="resultindicatorperiodactualcomment")


class ResultIndicatorPeriodXMLSerializer(SkipNullMixin, activity_serializers.ResultIndicatorPeriodSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*", read_only=True)
    actual = ResultIndicatorPeriodActualSerializer(source="*", read_only=True)

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


class ContactInfoXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ContactInfoSerializer):
    xml_meta = {'attributes': ('type', )}

    type = serializers.CharField(source='type.code')
    organisation = NarrativeContainerXMLSerializer()
    department = NarrativeContainerXMLSerializer()
    person_name = NarrativeContainerXMLSerializer()
    job_title = NarrativeContainerXMLSerializer()
    mailing_address = NarrativeContainerXMLSerializer()

    class Meta(activity_serializers.ContactInfoSerializer.Meta):
        fields = (
            'type',
            'organisation',
            'department',
            'person_name',
            'job_title',
            'telephone',
            'email',
            'website',
            'mailing_address',
        )


class CountryBudgetItemsXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.CountryBudgetItemsSerializer):
    xml_meta = {'attributes': ('vocabulary',)}

    vocabulary = serializers.CharField(source='vocabulary.code')

    class BudgetItemXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.BudgetItemSerializer.BudgetItemDescriptionSerializer):
        xml_meta = {'attributes': ('code',)}

        code = serializers.CharField(source='code.code')
        description = NarrativeContainerXMLSerializer()

        class Meta:
            model = iati_models.BudgetItem
            fields = (
                # 'budget_identifier',
                'code',
                'description',
            )

    budget_item = BudgetItemXMLSerializer(
        many=True,
        source="budgetitem_set")

    class Meta(activity_serializers.CountryBudgetItemsSerializer.Meta):
        fields = (
            'vocabulary',
            'budget_item',
        )

class LocationXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer):
    xml_meta = {'attributes': ('ref',)}

    location_reach = CodelistSerializer()

    class LocationIdXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.LocationIdSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary', )}
        vocabulary = serializers.CharField(source='location_id_vocabulary.code')

    location_id = LocationIdXMLSerializer(source='*')

    name = NarrativeContainerXMLSerializer()

    description = NarrativeContainerXMLSerializer()

    activity_description = NarrativeContainerXMLSerializer()

    class LocationAdministrativeXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.AdministrativeSerializer):
        xml_meta = {'attributes': ('code', 'vocabulary', 'level', )}
        vocabulary = serializers.CharField(source='vocabulary.code')

        class Meta:
            model = iati_models.LocationAdministrative
            fields = (
                'code',
                'vocabulary',
                'level',
            )

    administrative = LocationAdministrativeXMLSerializer(
        many=True,
        source="locationadministrative_set")

    class PointSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.LocationSerializer.PointSerializer):
        xml_meta = {'attributes': ('srsName',)}
        
        pos = PointIATIField(source='point_pos')
        #srsName = serializers.CharField(source="point_srs_name")

    point = PointSerializer(source="*")
    exactness = CodelistSerializer()

    location_class = CodelistSerializer()

    feature_designation = CodelistSerializer()

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

class ConditionsXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ConditionsSerializer):
    xml_meta = {'attributes': ('attached',)}
    attached = BoolToNumField()

    class ConditionXMLSerializer(XMLMetaMixin, SkipNullMixin, activity_serializers.ConditionSerializer):
        xml_meta = {'attributes': ('type', )}
        type = serializers.CharField(source='type.code')
        #test= NarrativeContainerXMLSerializer()
        narrative = NarrativeXMLSerializer(many=True, source='narratives')

        class Meta:
            model = iati_models.Condition
            fields = (
                'type',
                'narrative',
            )

    condition = ConditionXMLSerializer(
        many=True,
        source="condition_set")

    class Meta(activity_serializers.ConditionsSerializer.Meta):
        fields = (
            'attached',
            'condition',
        )

class TransactionProviderSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionProviderSerializer):
    xml_meta = {'attributes': ('ref', 'provider_activity_id', 'type')}

    type = CodelistSerializer()
    narrative = NarrativeXMLSerializer(many=True, source='narratives')


    class Meta(transaction_serializers.TransactionProviderSerializer.Meta):
        fields = (
            'ref',
            'provider_activity_id',
            'type',
            'narrative'
        )


class TransactionReceiverSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionReceiverSerializer):
    xml_meta = {'attributes': ('ref', 'receiver_activity_id', 'type')}

    type = CodelistSerializer()
    narrative = NarrativeXMLSerializer(many=True, source='narratives')


    class Meta(transaction_serializers.TransactionReceiverSerializer.Meta):
        fields = (
            'ref',
            'receiver_activity_id',
            'type',
            'narrative'
        )


class TransactionSectorXMLSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionSectorSerializer):
    xml_meta = {'attributes': ('code', 'vocabulary', 'vocabulary_uri')}

    code = serializers.CharField(source='sector.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField()

    class Meta(transaction_serializers.TransactionSectorSerializer.Meta):
        fields = (
            'code',
            'vocabulary',
            'vocabulary_uri',
        )

class TransactionRecipientCountryXMLSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionRecipientCountrySerializer):
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField(source='country.code')

    class Meta(transaction_serializers.TransactionRecipientCountrySerializer.Meta):
        fields = (
            'code',
        )

class TransactionRecipientRegionXMLSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionRecipientRegionSerializer):
    xml_meta = {'attributes': ('code', 'vocabulary', 'vocabulary_uri')}

    code = serializers.CharField(source='region.code')
    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.URLField(required=False)

    class Meta(transaction_serializers.TransactionRecipientRegionSerializer.Meta):
        fields = (
            'code',
            'vocabulary',
            'vocabulary_uri',
        )

class TransactionSerializer(XMLMetaMixin, SkipNullMixin, transaction_serializers.TransactionSerializer):
    xml_meta = {'attributes': ('ref', 'humanitarian',)}

    transaction_type = CodelistSerializer()
    description = NarrativeContainerXMLSerializer()
    provider_org = TransactionProviderSerializer(source='provider_organisation')
    receiver_org = TransactionReceiverSerializer(source='receiver_organisation')
    flow_type = CodelistSerializer()
    finance_type = CodelistSerializer()
    aid_type = CodelistSerializer()
    tied_status = CodelistSerializer()
    currency = CodelistSerializer()

    sector = TransactionSectorXMLSerializer(many=True, required=False, source="transactionsector_set")
    recipient_country = TransactionRecipientCountryXMLSerializer(many=True, required=False, source="transactionrecipientcountry_set")
    recipient_region = TransactionRecipientRegionXMLSerializer(many=True, required=False, source="transactionrecipientregion_set")

    value = ValueSerializer(source='*')
    transaction_date = IsoDateSerializer()
    disbursement_channel = CodelistSerializer()
    humanitarian = BoolToNumField()

    class Meta(transaction_serializers.TransactionSerializer.Meta):
        fields = (
            'ref',
            'humanitarian',
            'transaction_type',
            'transaction_date',
            'value',
            'description',
            'provider_org',
            'receiver_org',
            'disbursement_channel',
            'sector',
            'recipient_country',
            'recipient_region',
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

    other_identifier = OtherIdentifierXMLSerializer(many=True,source="otheridentifier_set", required=False)

    activity_status = CodelistSerializer()
    activity_date = ActivityDateSerializer(
        many=True,
        source='activitydate_set')

    contact_info = ContactInfoXMLSerializer(many=True, source="contactinfo_set")

    activity_scope = CodelistSerializer(source='scope')
    recipient_country = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set')
    recipient_region = ActivityRecipientRegionXMLSerializer(
        many=True,
        source='activityrecipientregion_set')
    location = LocationXMLSerializer(many=True, source='location_set')
    sector = ActivitySectorSerializer(
        many=True,
        source='activitysector_set')

    country_budget_items = CountryBudgetItemsXMLSerializer()

    humanitarian_scope = HumanitarianScopeXMLSerializer(many=True,source='humanitarianscope_set')

    policy_marker = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budget = BudgetSerializer(many=True, source='budget_set')
    planned_disbursement = PlannedDisbursementSerializer(many=True, source='planneddisbursement_set')
    
    capital_spend = CapitalSpendSerializer()
    transaction = TransactionSerializer(
        many=True,
        source='transaction_set')

    document_link = DocumentLinkXMLSerializer(
        many=True,
        source='documentlink_set')
    related_activity = RelatedActivitySerializer(
        many=True, 
        source='relatedactivity_set')

    legacy_data = LegacyDataXMLSerializer(many=True, source="legacydata_set")

    conditions = ConditionsXMLSerializer(many=True, source='conditions_set')

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
            'other_identifier',
            'activity_status',
            'activity_date',
            'contact_info',
            'activity_scope',
            'recipient_country',
            'recipient_region',
            'location',
            'sector',
            'country_budget_items',
            'humanitarian_scope',
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
            'legacy_data',
            'conditions',
            'result',
            # 'crs_add',
            # 'fss',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'humanitarian',
            'hierarchy',
            'linked_data_uri',
        )
