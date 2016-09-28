from rest_framework import serializers

from iati import models as iati_models
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
from api.activity.filters import RelatedActivityFilter

from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import NarrativeContainerSerializer
from api.codelist.serializers import NarrativeSerializer
from api.codelist.serializers import CodelistCategorySerializer

from iati.parser import validators
from iati.parser import exceptions

from django.db.models.fields.related import ManyToManyField, ManyToOneRel, OneToOneRel, ForeignKey

def get_or_raise(model, validated_data, attr, default=None):
    try:
        pk = validated_data.pop(attr)
    except KeyError:
        raise exceptions.RequiredFieldError(
                model.__name__,
                attr,
                )

    return model.objects.get(pk=pk)
    # except model.DoesNotExist:
    #     return default


def get_or_none(model, validated_data, attr, default=None):
    pk = validated_data.pop(attr, None)

    if pk is None:
        return default
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return default

def save_narratives(instance, data):
    current_narratives = instance.narratives.all()

    current_ids = set([ i.id for i in current_narratives ])
    new_ids = set([ i['id'] for i in data ])

    to_remove = list(current_ids.difference(new_ids))
    to_add = list(new_ids.difference(current_ids))
    to_update = list(current_ids.intersection(new_ids))

    for fk_id in to_update:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        for field, data in narrative_data.iteritems():
            setattr(narrative, field, data)
        narrative.save()

    for fk_id in to_add:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        iati_models.Narrative.create(related_object=instance, **narrative_data)

    for fk_id in to_remove:
        instance = iati_models.Narrative.objects.get(pk=fk_id)
        # instance = instances.get(pk=fk_id)
        instance.delete()

def handle_errors(validated):
    warnings = validated['warnings'] 
    errors = validated['errors'] 
    instance = validated['instance']

    if len(errors):
        for error in errors:
            raise ValidationError({
                error.field: error.message
                })

    return instance


class NestedWriteMixin():
    # def __init__(self, *args, **kwargs):
    #     super(NestedWriteMixin, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        model = getattr(self.Meta, 'model')

        fk_fields = []
        related_fields = []

        for field, data in validated_data.copy().iteritems():
            if (field in self.fields):
                if isinstance(model_field, (ManyToOneRel, ManyToManyField)):
                    related_fields[field] = validated_data.pop(field)
                elif isinstance(model_field, (ForeignKey, OneToOneRel)):
                    fk_fields[field] = validated_data.pop(field)

        # for field, data in related_fields.iteritems():


        for field, data in validated_data.iteritems():
            if (field in self.fields):

                source_serializer = self.fields[field]
                source_field = self.fields[field].source
                model_field = model._meta.get_field(source_field)
                field_model = model_field.related_model

                instance_data = getattr(instance, source_field)

                # # check if it is a related object serializer, handle accordingly
                if isinstance(model_field, (ManyToOneRel, ManyToManyField)):
                    if data is None:
                        # remove all related objects
                        instance_data.clear()
                    else:
                        # remove when i
                        related_set = instance_data

                        related_model_pk_field_name = field_model._meta.pk.name

                        # TODO: how do we get the serializer model? - 2016-09-13
                        serializer_model = None

                        # print(related_set.all())
                        # print(data)

                        current_ids = set([ i.id for i in related_set.all() ])
                        new_ids = set([ i[related_model_pk_field_name] for i in data ])

                        to_remove = list(current_ids.difference(new_ids))
                        to_add = list(new_ids.difference(current_ids))
                        to_update = list(current_ids.intersection(new_ids))

#                         print(to_remove)
#                         print(to_add)
#                         print(to_update)

                        # help(related_set)

                        for fk_id in to_remove:
                            obj = field_model.objects.get(pk=fk_id)
                            related_set.remove(obj)

                        for fk_id in to_add:
                            # TODO: instead call the serializer's create method - 2016-09-13
                            obj = field_model.objects.create(data)
                            related_set.add(obj)

                        for fk_id in to_update:
                            # TODO: call the serializer's update method - 2016-09-13
                            # needed for nested updating i guess
                            print('called')
                            fk_data = filter(lambda x: x[related_model_pk_field_name] is fk_id, data)[0]
                            serializer_class  = source_serializer.child
                            serializer.initial_data = fk_data
                            print(fk_data)
                            print(field_model.objects.get(pk=fk_id))
                            serializer.is_valid()
                            serializer.save()
                            pass

                # check if it is a foreign key, handle accordingly
                elif isinstance(model_field, (ForeignKey, OneToOneRel)):
                    if data is None:
                        # delete the fk object and set to
                        fk_id = instance_data
                        field_model.objects.get(pk=fk_id).remove()
                    else:
                        # set new foreign key
                        setattr(instance, field, data)

                else:
                    setattr(instance, field, data)

        instance.save()
        return instance

class ValueSerializer(serializers.Serializer):
    currency = CodelistSerializer()
    date = serializers.CharField(source='value_date')
    value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
            )

    class Meta:
        fields = (
                'value',
                'date',
                'currency',
                )


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.DocumentCategory
        fields = ('id', 'code', 'name')

        extra_kwargs = { "id": { "read_only": False }}

class DocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentDateSerializer(serializers.Serializer):
        iso_date = serializers.DateField()

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitle")
    document_date = DocumentDateSerializer(source="*")

    class Meta:
        model = iati_models.DocumentLink
        fields = (
            'id',
            'url',
            'format',
            'categories',
            'title',
            'document_date',
        )

        extra_kwargs = { "id": { "read_only": False }}


class CapitalSpendSerializer(serializers.ModelSerializer):
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='*',
        coerce_to_string=False
    )

    class Meta:
        model = iati_models.Activity
        fields = ('percentage',)


class BudgetSerializer(serializers.ModelSerializer):

    value = ValueSerializer(source='*')
    type = CodelistSerializer()
    status = CodelistSerializer()

    class Meta:
        model = iati_models.Budget
        # filter_class = BudgetFilter
        fields = (
            'id',
            'type',
            'status',
            'period_start',
            'period_end',
            'value',
        )

        extra_kwargs = { "id": { "read_only": False }}

class PlannedDisbursementSerializer(serializers.ModelSerializer):
    value = ValueSerializer(source='*')
    type = CodelistSerializer()

    class Meta:
        model = iati_models.PlannedDisbursement

        fields = (
            'id',
            'type',
            'period_start',
            'period_end',
            'value',
        )

        extra_kwargs = { "id": { "read_only": False }}


class ActivityDateSerializer(serializers.Serializer):
    type = CodelistSerializer()
    iso_date = serializers.DateTimeField()

    class Meta:
        model = iati_models.ActivityDate
        fields = ('id', 'iso_date', 'type')

        extra_kwargs = { "id": { "read_only": False }}


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


class ReportingOrganisationSerializer(DynamicFieldsModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source="normalized_ref")
    type = CodelistSerializer()
    secondary_reporter = serializers.BooleanField()
    # organisation = OrganisationSerializer()
    organisation = serializers.HyperlinkedRelatedField(view_name='organisations:organisation-detail', read_only=True)

    narratives = NarrativeSerializer(many=True, required=False)

    class Meta:
        model = iati_models.ActivityReportingOrganisation
        fields = (
            'id',
            'ref',
            'organisation',
            'type',
            'secondary_reporter',
            'narratives',
        )

class ReportingOrganisationSerializer(DynamicFieldsModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source="normalized_ref")
    type = CodelistSerializer()
    secondary_reporter = serializers.BooleanField()
    # organisation = OrganisationSerializer()
    organisation = serializers.HyperlinkedRelatedField(view_name='organisations:organisation-detail', read_only=True)

    activity = serializers.CharField(write_only=True)

    narratives = NarrativeSerializer(many=True, required=False)

    class Meta:
        model = iati_models.ActivityReportingOrganisation
        fields = (
            'id',
            'ref',
            'organisation',
            'type',
            'secondary_reporter',
            'narratives',
            'activity',
        )

    def create(self, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_reporting_org(
            activity,
            validated_data.get('normalized_ref'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('secondary_reporter')
        )
            
        instance = handle_errors(validated)
        instance.save()

        save_narratives(instance, narratives)

        return instance


    def update(self, instance, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_reporting_org(
            activity,
            validated_data.get('normalized_ref'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('secondary_reporter')
        )

        update_instance = handle_errors(validated)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance, narratives)

        return update_instance


class ParticipatingOrganisationSerializer(NestedWriteMixin, serializers.ModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = CodelistSerializer()
    role = CodelistSerializer()
    activity_id = serializers.CharField(source='org_activity_id', required=False)
    narratives = NarrativeSerializer(many=True, required=False)

    activity = serializers.CharField(write_only=True)

    def create(self, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_participating_org(
            activity,
            validated_data.get('normalized_ref'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('role', {}).get('code'),
            validated_data.get('activity_id')
        )
            
        instance = handle_errors(validated)
        instance.save()

        save_narratives(instance, narratives)

        return instance


    def update(self, instance, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_participating_org(
            activity,
            validated_data.get('normalized_ref'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('role', {}).get('code'),
            validated_data.get('activity_id')
        )

        update_instance = handle_errors(validated)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance, narratives)

        return update_instance

    class Meta:
        model = iati_models.ActivityParticipatingOrganisation
        fields = (
            'id',
            'ref',
            'type',
            'role',
            'activity_id',
            'activity',
            'narratives',
        )

class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    code = CodelistSerializer()
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.ActivityPolicyMarker
        fields = (
            'id',
            'narratives',
            'vocabulary',
            'vocabulary_uri',
            'significance',
            'code',
        )

        extra_kwargs = { "id": { "read_only": False }}


# TODO: change to NarrativeContainer
class TitleSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.Title
        fields = ('id', 'narratives',)

class DescriptionSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    activity = serializers.CharField(write_only=True)

    def create(self, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_description(
            activity,
            validated_data.get('type', {}).get('code'),
        )
            
        instance = handle_errors(validated)
        instance.save()

        save_narratives(instance, narratives)

        return instance


    def update(self, instance, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_description(
            activity,
            validated_data.get('type', {}).get('code'),
        )

        update_instance = handle_errors(validated)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance, narratives)

        return update_instance

    class Meta:
        model = iati_models.Description
        fields = (
            'id',
            'type',
            'narratives',
            'activity',
        )

class RelatedActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.RelatedActivityType
        fields = (
            'code',
            'name'
        )

        extra_kwargs = { "id": { "read_only": False }}

class RelatedActivitySerializer(serializers.ModelSerializer):
    ref_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    type = RelatedActivityTypeSerializer()

    class Meta:
        model = iati_models.RelatedActivity
        filter_class = RelatedActivityFilter
        fields = (
            'id',
            'ref_activity',
            'ref',
            'type',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ActivitySectorSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivitySector
        fields = (
            'id',
            'sector',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

        extra_kwargs = { "id": { "read_only": False }}


class ActivitySectorSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivitySector
        fields = (
            'id',
            'sector',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ActivityRecipientRegionSerializer(DynamicFieldsModelSerializer):
    region = RegionSerializer(
        fields=('url', 'code', 'name')
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivityRecipientRegion
        fields = (
            'id',
            'region',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

        extra_kwargs = { "id": { "read_only": False }}

class HumanitarianScopeSerializer(DynamicFieldsModelSerializer):
    type = CodelistSerializer() 
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    code = CodelistSerializer()

    class Meta:
        model = iati_models.HumanitarianScope
        fields = (
            'id',
            'type',
            'vocabulary',
            'vocabulary_uri',
            'code',
        )

        extra_kwargs = { "id": { "read_only": False }}

class RecipientCountrySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    # vocabulary = VocabularySerializer()

    class Meta:
        model = iati_models.ActivityRecipientCountry
        fields = (
            'id',
            'country',
            'percentage',
        )

        extra_kwargs = { "id": { "read_only": False }}


class ResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.ResultType
        fields = (
            'id',
            'code',
            'name',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ResultDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati_models.ResultDescription
        fields = (
            'id',
            'narratives',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ResultTitleSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati_models.ResultTitle
        fields = (
            'id',
            'narratives',
        )

        extra_kwargs = { "id": { "read_only": False }}



class ResultIndicatorPeriodLocationSerializer(serializers.Serializer):
    ref = serializers.CharField()

    class Meta:
        fields = (
            'ref',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ResultIndicatorPeriodDimensionSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.DecimalField(
        max_digits=25,
        decimal_places=10,
        coerce_to_string=False)

    class Meta:
        fields = (
            'name',
            'value',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ResultIndicatorPeriodTargetSerializer(serializers.Serializer):
    value = serializers.DecimalField(source='target', max_digits=25, decimal_places=10)
    comment = NarrativeContainerSerializer(source="resultindicatorperiodtargetcomment")
    location = ResultIndicatorPeriodLocationSerializer(many=True, source="resultindicatorperiodtargetlocation_set")
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodtargetdimension_set")

class ResultIndicatorPeriodActualSerializer(serializers.Serializer):
    value = serializers.DecimalField(source='actual', max_digits=25, decimal_places=10)
    comment = NarrativeContainerSerializer(source="resultindicatorperiodactualcomment")
    location = ResultIndicatorPeriodLocationSerializer(many=True, source="resultindicatorperiodactuallocation_set")
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodactualdimension_set")

class ResultIndicatorPeriodSerializer(serializers.ModelSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*")
    actual = ResultIndicatorPeriodActualSerializer(source="*")

    class Meta:
        model = iati_models.ResultIndicatorPeriod
        fields = (
            'id',
            'period_start',
            'period_end',
            'target',
            'actual',
        )

        extra_kwargs = { "id": { "read_only": False }}

class ResultIndicatorBaselineSerializer(serializers.Serializer):
    year = serializers.CharField(source='baseline_year')
    value = serializers.CharField(source='baseline_value')
    comment = NarrativeContainerSerializer(source="resultindicatorbaselinecomment")

class ResultIndicatorSerializer(serializers.ModelSerializer):
    title = NarrativeContainerSerializer(source="resultindicatortitle")
    description = NarrativeContainerSerializer(source="resultindicatordescription")
    #  TODO 2.02 reference = ? 
    baseline = ResultIndicatorBaselineSerializer(source="*")
    period = ResultIndicatorPeriodSerializer(source='resultindicatorperiod_set', many=True)
    measure = CodelistSerializer()

    class Meta:
        model = iati_models.ResultIndicator
        fields = (
            'id',
            'title',
            'description',
            'baseline',
            'period',
            'measure',
            'ascending'
        )

        extra_kwargs = { "id": { "read_only": False }}


class ContactInfoSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    organisation = NarrativeContainerSerializer()
    department = NarrativeContainerSerializer()
    person_name = NarrativeContainerSerializer()
    job_title = NarrativeContainerSerializer()
    mailing_address = NarrativeContainerSerializer()

    class Meta:
        model = iati_models.ContactInfo
        fields = (
            'id',
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

        extra_kwargs = { "id": { "read_only": False }}

class ResultSerializer(serializers.ModelSerializer):
    type = CodelistSerializer() 
    title = NarrativeContainerSerializer(source="resulttitle")
    description = NarrativeContainerSerializer(source="resultdescription")
    indicator = ResultIndicatorSerializer(source='resultindicator_set', many=True)

    class Meta:
        model = iati_models.Result
        fields = (
            'id',
            'title',
            'description',
            'indicator',
            'type',
            'aggregation_status',
        )

        extra_kwargs = { "id": { "read_only": False }}

class LocationSerializer(serializers.ModelSerializer):
    class LocationIdSerializer(serializers.Serializer):
        vocabulary = VocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')

    class PointSerializer(serializers.Serializer):
        pos = PointField(source='point_pos')
        srsName = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(serializers.ModelSerializer):
        code = serializers.CharField()
        vocabulary = VocabularySerializer()

        class Meta:
            model = iati_models.LocationAdministrative
            fields = (
                'id',
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
    
    class Meta:
        model = iati_models.Location
        fields = (
            'id',
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

        extra_kwargs = { "id": { "read_only": False }}

class ActivityAggregationContainerSerializer(DynamicFieldsSerializer):
    activity = ActivityAggregationSerializer(source='activity_aggregation')
    children = ActivityAggregationSerializer(source='child_aggregation')
    activity_children = ActivityAggregationSerializer(source='activity_plus_child_aggregation')


class ActivitySerializer(NestedWriteMixin, DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail', read_only=True)
    iati_identifier = serializers.CharField()
    reporting_organisations = ReportingOrganisationSerializer(
        many=True
    )
    title = TitleSerializer()
    descriptions = DescriptionSerializer(
        many=True, 
        source='description_set'
    )
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True,
    )

    # TODO ; add other-identifier serializer
    # other_identifier = serializers.OtherIdentifierSerializer(many=True,source="?")

    activity_status = CodelistSerializer()
    activity_dates = ActivityDateSerializer(
        many=True,
        source='activitydate_set')

    # TODO ; add contact-info serializer
    # note; contact info has a sequence we should use in the ContactInfoSerializer!
    contact_info = ContactInfoSerializer(many=True, source="contactinfo_set")

    activity_scope = CodelistSerializer(source='scope')
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set')
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activityrecipientregion_set')
    locations = LocationSerializer(many=True, source='location_set')
    sectors = ActivitySectorSerializer(
        many=True,
        source='activitysector_set')

    # TODO ; add country-budget-items serializer
    # country_budget_items = serializers.CountryBudgetItemsSerializer(many=True,source="?")

    humanitarian_scope = HumanitarianScopeSerializer(many=True, source='humanitarianscope_set')

    policy_markers = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budgets = BudgetSerializer(many=True, source='budget_set')

    # note; planned-disbursement has a sequence in PlannedDisbursementSerializer
    planned_disbursements = PlannedDisbursementSerializer(many=True, source='planneddisbursement_set')

    capital_spend = CapitalSpendSerializer()

    transactions = serializers.HyperlinkedIdentityField(
        view_name='activities:activity-transactions',)
    # transactions = TransactionSerializer(
    #     many=True,
    #     source='transaction_set')

    document_links = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    related_activities = RelatedActivitySerializer(
        many=True, 
        source='relatedactivity_set')

    # TODO ; add legacy-data serializer? note: we dont parse legacy data atm.
    # legacy_data = LegacyDataSerializer(many=True, source="?")

    # TODO ; add conditions serializer
    # conditions = serializers.ConditionsSerializer(many=True,source="?")

    results = ResultSerializer(many=True, source="result_set")
    
    # TODO ; add crs-add serializer
    # note; crs-add has a sequence in CrsAddSerializer
    # crs_add = serializers.CrsAddSerializer(many=True, source="?")

    # TODO ; add fss serializer
    # fss = serializers.FssSerializer(many=True, source="?") 
    
    # activity attributes
    last_updated_datetime = serializers.DateTimeField()
    xml_lang = serializers.CharField(source='default_lang')
    default_currency = CodelistSerializer()

    humanitarian = serializers.BooleanField()

    # other added data
    aggregations = ActivityAggregationContainerSerializer(source="*", read_only=True)

    def create(self, validated_data):
        validated = validators.activity(
            validated_data.get('iati_identifier'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('role', {}).get('code'),
            validated_data.get('activity_id')
        )
            
        instance = handle_errors(validated)
        instance.save()

        save_narratives(instance, narratives)

        return instance


    def update(self, instance, validated_data):
        activity = get_or_raise(iati_models.Activity, validated_data, 'activity')
        narratives = get_or_none(iati_models.Activity, validated_data, 'narratives', [])

        validated = validators.activity_participating_org(
            activity,
            validated_data.get('normalized_ref'),
            validated_data.get('type', {}).get('code'),
            validated_data.get('role', {}).get('code'),
            validated_data.get('activity_id')
        )

        update_instance = handle_errors(validated)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance, narratives)

        return update_instance

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'reporting_organisations',
            'title',
            'descriptions',
            'participating_organisations',
            # 'other_identifier',
            'activity_status',
            'activity_dates',
            'contact_info',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'locations',
            'sectors',
            # 'country_budget_items',
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
            # 'legacy_data',
            # 'conditions',
            'results',
            # 'crs_add',
            # 'fss',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'humanitarian',
            'hierarchy',
            'linked_data_uri',
            'aggregations',
            'xml_source_ref',
        )


class CheckValidIATIMixin():

    def save(self, *args, **kwargs):
        instance = super(CheckValidIATIMixin, self).save(*args, **kwargs)

        # query activity and check if it is valid or not

        activity = instance.activity

        if (activity.is_valid_iati)

        activity.is_valid_iati = True
        activity.save()

        # check if activity has the required fields set


        
