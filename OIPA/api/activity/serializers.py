from rest_framework import serializers

from iati import models as iati_models
from iati_codelists import models as iati_codelists_models

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer, BasicRegionSerializer
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

from api.generics.utils import get_or_raise, get_or_none

def save_narratives(instance, data, activity_instance):
    current_narratives = instance.narratives.all()

    current_ids = set([ i.id for i in current_narratives ])
    old_ids = set(filter(lambda x: x is not None, [ i.get('id') for i in data ]))
    new_data = filter(lambda x: x.get('id') is None, data)

    # print(current_ids)
    # print(old_ids)
    # print(new_data)

    to_remove = list(current_ids.difference(old_ids))
    # to_add = list(new_ids.difference(current_ids))
    to_add = new_data
    to_update = list(current_ids.intersection(old_ids))

    for fk_id in to_update:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        for field, data in narrative_data.iteritems():
            setattr(narrative, field, data)
        narrative.save()

    for fk_id in to_remove:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        # instance = instances.get(pk=fk_id)
        narrative.delete()

    for narrative_data in to_add:
        # narrative = iati_models.Narrative.objects.get(pk=fk_id)
        # narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        iati_models.Narrative.objects.create(
                related_object=instance, 
                activity=activity_instance,
                **narrative_data)

def handle_errors(validated, **rest_validated):
    warnings = validated['warnings'] # a list
    errors = validated['errors']
    validated_data = validated['validated_data'] # a dict

    error_dict = {}

    for error in errors:
        error_dict[error.field] = error.message


    for key, vals in rest_validated.iteritems():

        validated_data.update({
            key: vals['validated_data']
        })

        if len(vals['errors']):
            error_dict[key] = vals['errors']
            # for error in vals['errors']:
            #     error_dict[error.field] = error.message

    if len(error_dict):
        raise ValidationError(error_dict)
        
    return validated_data

#     validated_data.update({ "narratives": narrative_validated_data })

# def handle_errors(validated, validated_narratives=None):
#     warnings = validated['warnings'] # a list
#     errors = validated['errors']
#     validated_data = validated['validated_data'] # a dict

#     error_dict = {}

#     if len(errors):
#         for error in errors:
#             error_dict[error.field] = error.message

#     if validated_narratives:
#         narrative_warnings = validated_narratives['warnings']
#         narrative_errors = validated_narratives['errors']
#         narrative_validated_data = validated_narratives['validated_data']

#         if len(narrative_errors):
#             for error in narrative_errors:
#                 error_dict[error.field] = error.message

#         if len(error_dict):
#             raise ValidationError(error_dict)

#         validated_data.update({ "narratives": narrative_validated_data })

#     return validated_data


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
                            fk_data = filter(lambda x: x[related_model_pk_field_name] is fk_id, data)[0]
                            serializer_class  = source_serializer.child
                            serializer.initial_data = fk_data
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
        fields = ('code', 'name')

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

    activity = serializers.CharField(write_only=True)

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    class Meta:
        model = iati_models.Budget
        # filter_class = BudgetFilter
        fields = (
            'activity',
            'id',
            'type',
            'status',
            'period_start',
            'period_end',
            'value',
        )

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_budget(
            activity,
            data.get('type', {}).get('code'),
            data.get('status', {}).get('code'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        instance = iati_models.Budget.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        update_instance = iati_models.Budget(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

class PlannedDisbursementProviderSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(source="normalized_ref")
    organisation = serializers.PrimaryKeyRelatedField(queryset=iati_models.Organisation.objects.all(), required=False)
    type = CodelistSerializer()
    provider_activity = serializers.PrimaryKeyRelatedField(queryset=iati_models.Activity.objects.all(), required=False)
    narratives = NarrativeSerializer(many=True, required=False)

    class Meta:
        model = iati_models.PlannedDisbursementProvider

        fields = (
                'ref',
                'organisation',
                'type',
                'provider_activity',
                'narratives',
                )

        validators = []

class PlannedDisbursementReceiverSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(source="normalized_ref")
    organisation = serializers.PrimaryKeyRelatedField(queryset=iati_models.Organisation.objects.all(), required=False)
    type = CodelistSerializer()
    receiver_activity = serializers.PrimaryKeyRelatedField(queryset=iati_models.Activity.objects.all(), required=False)
    narratives = NarrativeSerializer(many=True, required=False)

    class Meta:
        model = iati_models.PlannedDisbursementReceiver

        fields = (
                'ref',
                'organisation',
                'type',
                'receiver_activity',
                'narratives',
                )

        validators = []

class PlannedDisbursementSerializer(serializers.ModelSerializer):
    value = ValueSerializer(source='*')
    type = CodelistSerializer()

    activity = serializers.CharField(write_only=True)

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    provider_organisation = PlannedDisbursementProviderSerializer(required=False)
    receiver_organisation = PlannedDisbursementReceiverSerializer(required=False)

    class Meta:
        model = iati_models.PlannedDisbursement

        fields = (
            'activity',
            'id',
            'type',
            'period_start',
            'period_end',
            'value',
            'provider_organisation',
            'receiver_organisation',
        )

        validators = []

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_planned_disbursement(
            activity,
            data.get('type', {}).get('code'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('currency', {}).get('code'),
            data.get('value_date'),
            data.get('value'),
            data.get('provider_organisation', {}).get('normalized_ref'),
            data.get('provider_organisation', {}).get('provider_activity'),
            data.get('provider_organisation', {}).get('type', {}).get('code'),
            data.get('provider_organisation', {}).get('narratives'),
            data.get('receiver_organisation', {}).get('normalized_ref'),
            data.get('receiver_organisation', {}).get('receiver_activity'),
            data.get('receiver_organisation', {}).get('type', {}).get('code'),
            data.get('receiver_organisation', {}).get('narratives'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        activity = validated_data.get('activity')
        provider_data = validated_data.pop('provider_org')
        provider_narratives_data = validated_data.pop('provider_org_narratives', [])
        receiver_data = validated_data.pop('receiver_org')
        receiver_narratives_data = validated_data.pop('receiver_org_narratives', [])

        # print(provider_data)

        instance = iati_models.PlannedDisbursement.objects.create(**validated_data)

        if provider_data['ref']:
            provider_org = iati_models.PlannedDisbursementProvider.objects.create(
                    planned_disbursement=instance,
                    **provider_data)
            save_narratives(provider_org, provider_narratives_data, activity)
            validated_data['provider_organisation'] = provider_org
        if receiver_data['ref']:
            receiver_org = iati_models.PlannedDisbursementReceiver.objects.create(
                    planned_disbursement=instance,
                    **receiver_data)
            save_narratives(receiver_org, receiver_narratives_data, activity)
            validated_data['receiver_organisation'] = receiver_org

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        provider_organisation_data = validated_data.pop('provider_org')
        provider_organisation_narratives_data = validated_data.pop('provider_org_narratives')
        receiver_organisation_data = validated_data.pop('receiver_org')
        receiver_organisation_narratives_data = validated_data.pop('receiver_org_narratives')

        update_instance = iati_models.PlannedDisbursement(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        # save_narratives(update_instance, narratives, activity)

        return update_instance


class ActivityDateSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    iso_date = serializers.DateTimeField()

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_activity_date(
            activity,
            data.get('type', {}).get('code'),
            data.get('iso_date'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        instance = iati_models.ActivityDate.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')

        update_instance = iati_models.ActivityDate(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

    class Meta:
        model = iati_models.ActivityDate
        fields = ('id', 'activity', 'iso_date', 'type')


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

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')
        # narratives = data.pop('narratives', [])

        validated = validators.activity_reporting_org(
            activity,
            data.get('normalized_ref'),
            data.get('type', {}).get('code'),
            data.get('secondary_reporter'),
            data.get('narratives')
        )

        # validated_narratives = validators.narratives(activity, narratives)

        return handle_errors(validated)


    def create(self, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        instance = iati_models.ActivityReportingOrganisation.objects.create(**validated_data)

        save_narratives(instance, narratives, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        update_instance = iati_models.ActivityReportingOrganisation(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance, narratives, activity)

        return update_instance


class ParticipatingOrganisationSerializer(NestedWriteMixin, serializers.ModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = CodelistSerializer()
    role = CodelistSerializer()
    activity_id = serializers.CharField(source='org_activity_id', required=False)
    narratives = NarrativeSerializer(many=True, required=False)

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_participating_org(
            activity,
            data.get('normalized_ref'),
            data.get('type', {}).get('code'),
            data.get('role', {}).get('code'),
            data.get('activity_id'),
            data.get('narratives')
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        instance = iati_models.ActivityParticipatingOrganisation.objects.create(**validated_data)

        save_narratives(instance, narratives, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        update_instance = iati_models.ActivityParticipatingOrganisation(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance, narratives, activity)

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
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    policy_marker = CodelistSerializer(source="code")
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_policy_marker(
            activity,
            data.get('vocabulary', {}).get('code'),
            data.get('vocabulary_uri'),
            data.get('code', {}).get('code'),
            data.get('significance', {}).get('code'),
            data.get('narratives')
        )

        return handle_errors(validated)


    def create(self, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        instance = iati_models.ActivityPolicyMarker.objects.create(**validated_data)

        save_narratives(instance, narratives, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        update_instance = iati_models.ActivityPolicyMarker(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance, narratives, activity)

        return update_instance

    class Meta:
        model = iati_models.ActivityPolicyMarker
        fields = (
            'activity',
            'id',
            'vocabulary',
            'vocabulary_uri',
            'policy_marker',
            'significance',
            'narratives',
        )


# TODO: change to NarrativeContainer
class TitleSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

    # def validate(self, data):
    #     activity = get_or_raise(iati_models.Activity, data, 'activity')
    #     narratives = data.pop('narratives', [])

    #     print('goggo')

    #     validated = validators.activity_title(
    #         activity,
    #         narratives,
    #     )

    #     return handle_errors(validated)

    # def create(self, validated_data):
    #     narratives = validated_data.pop('narratives', [])

    #     instance = iati_models.Title.objects.create(**validated_data)

    #     save_narratives(instance, narratives)

    #     return instance


    # def update(self, instance, validated_data):
    #     narratives = validated_data.pop('narratives', [])

    #     update_instance = iati_models.Title(**validated_data)
    #     update_instance.id = instance.id
    #     update_instance.save()

    #     save_narratives(instance, narratives)

    #     return update_instance

    class Meta:
        model = iati_models.Title
        fields = ('id', 'narratives',)

class DescriptionSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_description(
            activity,
            data.get('type', {}).get('code'),
            data.get('narratives')
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        instance = iati_models.Description.objects.create(**validated_data)

        save_narratives(instance, narratives, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        narratives = validated_data.pop('narratives', [])

        update_instance = iati_models.Description(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance, narratives, activity)

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

class ActivityRecipientRegionSerializer(DynamicFieldsModelSerializer):
    region = BasicRegionSerializer(
        fields=('url', 'code', 'name'),
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField(required=False)

    activity = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.ActivityRecipientRegion
        fields = (
            'id',
            'activity',
            'region',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_recipient_region(
            activity,
            data.get('region', {}).get('code'),
            data.get('vocabulary', {}).get('code'),
            data.get('vocabulary_uri'),
            data.get('percentage'),
            getattr(self, 'instance', None), # only on update
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        instance = iati_models.ActivityRecipientRegion.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')

        update_instance = iati_models.ActivityRecipientRegion(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

class HumanitarianScopeSerializer(DynamicFieldsModelSerializer):
    type = CodelistSerializer() 
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    # code = CodelistSerializer()
    code = serializers.CharField()

    activity = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.HumanitarianScope
        fields = (
            'activity',
            'id',
            'type',
            'vocabulary',
            'vocabulary_uri',
            'code',
        )

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_humanitarian_scope(
            activity,
            data.get('type', {}).get('code'),
            data.get('vocabulary', {}).get('code'),
            data.get('vocabulary_uri'),
            data.get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        instance = iati_models.HumanitarianScope.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        update_instance = iati_models.HumanitarianScope(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

class RecipientCountrySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_recipient_country(
            activity,
            data.get('country', {}).get('code'),
            data.get('percentage'),
            getattr(self, 'instance', None), # only on update
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        instance = iati_models.ActivityRecipientCountry.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')

        update_instance = iati_models.ActivityRecipientCountry(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

    class Meta:
        model = iati_models.ActivityRecipientCountry
        fields = (
            'id',
            'activity',
            'country',
            'percentage',
        )


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



class ResultIndicatorPeriodActualLocationSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    result_indicator_period = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.ResultIndicatorPeriodActualLocation
        fields = (
            'result_indicator_period',
            'ref',
        )

    def validate(self, data):
        result_indicator_period = get_or_raise(iati_models.ResultIndicatorPeriod, data, 'result_indicator_period')

        validated = validators.activity_result_indicator_period_location(
            result_indicator_period,
            data.get('ref'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        instance = iati_models.ResultIndicatorPeriodActualLocation.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        update_instance = iati_models.ResultIndicatorPeriodActualLocation(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

class ResultIndicatorPeriodTargetLocationSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()

    class Meta:
        model = iati_models.ResultIndicatorPeriodTargetLocation
        fields = (
            'ref',
        )

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
    location = ResultIndicatorPeriodTargetLocationSerializer(many=True, source="resultindicatorperiodtargetlocation_set", required=False)
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodtargetdimension_set", required=False)

class ResultIndicatorPeriodActualSerializer(serializers.Serializer):
    value = serializers.DecimalField(source='actual', max_digits=25, decimal_places=10)
    comment = NarrativeContainerSerializer(source="resultindicatorperiodactualcomment")
    location = ResultIndicatorPeriodActualLocationSerializer(many=True, source="resultindicatorperiodactuallocation_set", required=False)
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodactualdimension_set", required=False)

class ResultIndicatorPeriodSerializer(serializers.ModelSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*")
    actual = ResultIndicatorPeriodActualSerializer(source="*")

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    result_indicator = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.ResultIndicatorPeriod
        fields = (
            'result_indicator',
            'id',
            'period_start',
            'period_end',
            'target',
            'actual',
        )

    def validate(self, data):
        result_indicator = get_or_raise(iati_models.ResultIndicator, data, 'result_indicator')

        validated = validators.activity_result_indicator_period(
            result_indicator,
            data.get('target'),
            data.get('actual'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('resultindicatorperiodtargetcomment').get('narratives'),
            data.get('resultindicatorperiodactualcomment').get('narratives'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        result_indicator = validated_data.get('result_indicator')
        target_comment_narratives_data = validated_data.pop('target_comment_narratives', [])
        actual_comment_narratives_data = validated_data.pop('actual_comment_narratives', [])

        instance = iati_models.ResultIndicatorPeriod.objects.create(**validated_data)

        target_comment_narratives = iati_models.ResultIndicatorPeriodTargetComment.objects.create(result_indicator_period=instance)
        actual_comment_narratives = iati_models.ResultIndicatorPeriodActualComment.objects.create(result_indicator_period=instance)

        save_narratives(target_comment_narratives, target_comment_narratives_data, result_indicator.result.activity)
        save_narratives(actual_comment_narratives, actual_comment_narratives_data, result_indicator.result.activity)

        return instance

    def update(self, instance, validated_data):
        result_indicator = validated_data.get('result_indicator')
        target_comment_narratives_data = validated_data.pop('target_comment_narratives', [])
        actual_comment_narratives_data = validated_data.pop('actual_comment_narratives', [])

        update_instance = iati_models.ResultIndicatorPeriod(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance.resultindicatorperiodtargetcomment, target_comment_narratives_data, result_indicator.result.activity)
        save_narratives(update_instance.resultindicatorperiodactualcomment, actual_comment_narratives_data, result_indicator.result.activity)

        return update_instance

class ResultIndicatorBaselineSerializer(serializers.Serializer):
    year = serializers.CharField(source='baseline_year')
    value = serializers.CharField(source='baseline_value')
    comment = NarrativeContainerSerializer(source="resultindicatorbaselinecomment")

class ResultIndicatorReferenceSerializer(serializers.ModelSerializer):
    vocabulary = VocabularySerializer()
    code = serializers.CharField()

    result_indicator = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.ResultIndicatorReference
        fields = (
            'result_indicator',
            'id',
            'vocabulary',
            'code',
            'indicator_uri',
        )

    def validate(self, data):
        result_indicator = get_or_raise(iati_models.ResultIndicator, data, 'result_indicator')

        validated = validators.activity_result_indicator_reference(
            result_indicator,
            data.get('vocabulary', {}).get('code'),
            data.get('code'),
            data.get('indicator_uri'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        instance = iati_models.ResultIndicatorReference.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        update_instance = iati_models.ResultIndicatorReference(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance

class ResultIndicatorSerializer(serializers.ModelSerializer):
    title = NarrativeContainerSerializer(source="resultindicatortitle")
    description = NarrativeContainerSerializer(source="resultindicatordescription")
    #  TODO 2.02 reference = ? 
    reference = ResultIndicatorReferenceSerializer(source='resultindicatorreference_set', many=True, required=False)
    baseline = ResultIndicatorBaselineSerializer(source="*")
    period = ResultIndicatorPeriodSerializer(source='resultindicatorperiod_set', many=True, required=False)
    measure = CodelistSerializer()

    result = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.ResultIndicator
        fields = (
            'result',
            'id',
            'title',
            'description',
            'reference',
            'baseline',
            'period',
            'measure',
            'ascending'
        )

    def validate(self, data):
        result = get_or_raise(iati_models.Result, data, 'result')

        validated = validators.activity_result_indicator(
            result,
            data.get('measure', {}).get('code'),
            data.get('ascending'),
            data.get('resultindicatortitle', {}).get('narratives'),
            data.get('resultindicatordescription', {}).get('narratives'),
            data.get('baseline_year'),
            data.get('baseline_value'),
            data.get('resultindicatorbaselinecomment', {}).get('narratives'),
            # data.get('baseline', {}).get('year'),
            # data.get('baseline', {}).get('value'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        result = validated_data.get('result')
        title_narratives_data = validated_data.pop('title_narratives', [])
        description_narratives_data = validated_data.pop('description_narratives', [])
        baseline_comment_narratives_data = validated_data.pop('baseline_comment_narratives', [])

        instance = iati_models.ResultIndicator.objects.create(**validated_data)

        result_indicator_title = iati_models.ResultIndicatorTitle.objects.create(result_indicator=instance)
        result_indicator_description = iati_models.ResultIndicatorDescription.objects.create(result_indicator=instance)
        result_indicator_baseline_comment = iati_models.ResultIndicatorBaselineComment.objects.create(result_indicator=instance)

        save_narratives(result_indicator_title, title_narratives_data, result.activity)
        save_narratives(result_indicator_description, description_narratives_data, result.activity)
        save_narratives(result_indicator_baseline_comment, baseline_comment_narratives_data, result.activity)

        return instance


    def update(self, instance, validated_data):
        result = validated_data.get('result')
        title_narratives_data = validated_data.pop('title_narratives', [])
        description_narratives_data = validated_data.pop('description_narratives', [])
        baseline_comment_narratives_data = validated_data.pop('baseline_comment_narratives', [])

        update_instance = iati_models.ResultIndicator(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(instance.resultindicatortitle, title_narratives_data, result.activity)
        save_narratives(instance.resultindicatordescription, description_narratives_data, result.activity)
        save_narratives(instance.resultindicatorbaselinecomment, baseline_comment_narratives_data, result.activity)

        return update_instance


class ContactInfoSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    organisation = NarrativeContainerSerializer()
    department = NarrativeContainerSerializer()
    person_name = NarrativeContainerSerializer()
    job_title = NarrativeContainerSerializer()
    mailing_address = NarrativeContainerSerializer()

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_contact_info(
            activity,
            data.get('type', {}).get('code'),
            data.get('organisation'),
            data.get('department'),
            data.get('person_name'),
            data.get('job_title'),
            data.get('telephone'), # text
            data.get('email'), # text
            data.get('website'), # text
            data.get('mailing_address'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')

        organisation_data = validated_data.pop('organisation', None)
        organisation_narratives_data = validated_data.pop('organisation_narratives', None)
        department_data = validated_data.pop('department', None)
        department_narratives_data = validated_data.pop('department_narratives', None)
        person_name_data = validated_data.pop('person_name', None)
        person_name_narratives_data = validated_data.pop('person_name_narratives', None)
        job_title_data = validated_data.pop('job_title', None)
        job_title_narratives_data = validated_data.pop('job_title_narratives', None)
        mailing_address_data = validated_data.pop('mailing_address', None)
        mailing_address_narratives_data = validated_data.pop('mailing_address_narratives', None)

        instance = iati_models.ContactInfo.objects.create(**validated_data)

        if organisation_data is not None:
            organisation = iati_models.ContactInfoOrganisation.objects.create(
                    contact_info=instance,
                    **organisation_data)
            instance.organisation = organisation

            if organisation_narratives_data:
                save_narratives(organisation, organisation_narratives_data, activity)

        if department_data is not None:
            department = iati_models.ContactInfoDepartment.objects.create(
                    contact_info=instance,
                    **department_data)
            instance.department = department

            if department_narratives_data:
                save_narratives(department, department_narratives_data, activity)

        if person_name_data is not None:
            person_name = iati_models.ContactInfoPersonName.objects.create(
                    contact_info=instance,
                    **person_name_data)
            instance.person_name = person_name

            if person_name_narratives_data:
                save_narratives(person_name, person_name_narratives_data, activity)

        if job_title_data is not None:
            job_title = iati_models.ContactInfoJobTitle.objects.create(
                    contact_info=instance,
                    **job_title_data)
            instance.job_title = job_title

            if job_title_narratives_data:
                save_narratives(job_title, job_title_narratives_data, activity)

        if mailing_address_data is not None:
            mailing_address = iati_models.ContactInfoMailingAddress.objects.create(
                    contact_info=instance,
                    **mailing_address_data)
            instance.mailing_address = mailing_address

            if mailing_address_narratives_data:
                save_narratives(mailing_address, mailing_address_narratives_data, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        organisation_data = validated_data.pop('organisation', None)
        organisation_narratives_data = validated_data.pop('organisation_narratives', None)
        department_data = validated_data.pop('department', None)
        department_narratives_data = validated_data.pop('department_narratives', None)
        person_name_data = validated_data.pop('person_name', None)
        person_name_narratives_data = validated_data.pop('person_name_narratives', None)
        job_title_data = validated_data.pop('job_title', None)
        job_title_narratives_data = validated_data.pop('job_title_narratives', None)
        mailing_address_data = validated_data.pop('mailing_address', None)
        mailing_address_narratives_data = validated_data.pop('mailing_address_narratives', None)

        update_instance = iati_models.ContactInfo(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        if organisation_data is not None:
            organisation = iati_models.ContactInfoOrganisation.objects.create(
                    contact_info=instance,
                    **organisation_data)
            update_instance.organisation = organisation

            if organisation_narratives_data:
                save_narratives(organisation, organisation_narratives_data, activity)

        if department_data is not None:
            department = iati_models.ContactInfoDepartment.objects.create(
                    contact_info=instance,
                    **department_data)
            update_instance.department = department

            if department_narratives_data:
                save_narratives(department, department_narratives_data, activity)

        if person_name_data is not None:
            person_name = iati_models.ContactInfoPersonName.objects.create(
                    contact_info=instance,
                    **person_name_data)
            update_instance.person_name = person_name

            if person_name_narratives_data:
                save_narratives(person_name, person_name_narratives_data, activity)

        if job_title_data is not None:
            job_title = iati_models.ContactInfoJobTitle.objects.create(
                    contact_info=instance,
                    **job_title_data)
            update_instance.job_title = job_title

            if job_title_narratives_data:
                save_narratives(job_title, job_title_narratives_data, activity)

        if mailing_address_data is not None:
            mailing_address = iati_models.ContactInfoMailingAddress.objects.create(
                    contact_info=instance,
                    **mailing_address_data)
            update_instance.mailing_address = mailing_address

            if mailing_address_narratives_data:
                save_narratives(mailing_address, mailing_address_narratives_data, activity)

        return update_instance

    class Meta:
        model = iati_models.ContactInfo
        fields = (
            'id',
            'activity',
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

class ResultSerializer(serializers.ModelSerializer):
    type = CodelistSerializer() 
    title = NarrativeContainerSerializer(source="resulttitle")
    description = NarrativeContainerSerializer(source="resultdescription")
    indicator = ResultIndicatorSerializer(source='resultindicator_set', many=True, required=False)

    activity = serializers.CharField(write_only=True)

    class Meta:
        model = iati_models.Result
        fields = (
            'activity',
            'id',
            'title',
            'description',
            'indicator',
            'type',
            'aggregation_status',
        )

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        validated = validators.activity_result(
            activity,
            data.get('type', {}).get('code'),
            data.get('aggregation_status'),
            data.get('resulttitle', {}).get('narratives'),
            data.get('resultdescription', {}).get('narratives'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        activity = validated_data.get('activity')
        title_narratives_data = validated_data.pop('title_narratives', [])
        description_narratives_data = validated_data.pop('description_narratives', [])

        instance = iati_models.Result.objects.create(**validated_data)

        result_title = iati_models.ResultTitle.objects.create(result=instance)
        result_description = iati_models.ResultDescription.objects.create(result=instance)

        save_narratives(result_title, title_narratives_data, activity)
        save_narratives(result_description, description_narratives_data, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        title_narratives_data = validated_data.pop('title_narratives', [])
        description_narratives_data = validated_data.pop('description_narratives', [])

        update_instance = iati_models.Result(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance.resulttitle, title_narratives_data, activity)
        save_narratives(update_instance.resultdescription, description_narratives_data, activity)

        return update_instance


class LocationSerializer(DynamicFieldsModelSerializer):
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
    name = NarrativeContainerSerializer()
    description = NarrativeContainerSerializer()
    activity_description = NarrativeContainerSerializer()

    # administrative has its own view
    administrative = AdministrativeSerializer(
            many=True,
            source="locationadministrative_set",
            read_only=True
        )

    point = PointSerializer(source="*")
    exactness = CodelistSerializer()
    location_class = CodelistSerializer()
    feature_designation = CodelistSerializer()

    activity = serializers.CharField(write_only=True)

    def validate(self, data):
        activity = get_or_raise(iati_models.Activity, data, 'activity')

        # print(data)
        # print('called...')
        # print(data.get('point'))

        validated = validators.activity_location(
            activity,
            data.get('ref'),
            data.get('location_reach', {}).get('code'),
            data.get('location_id_code', {}),
            data.get('location_id_vocabulary', {}).get('code'),
            data.get('name', {}).get('narratives'),
            data.get('description', {}).get('narratives'),
            data.get('activity_description', {}).get('narratives'),
            data.get('point_srs_name', {}),
            data.get('point_pos', {}),
            data.get('exactness', {}).get('code'),
            data.get('location_class', {}).get('code'),
            data.get('feature_designation', {}).get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')
        name_narratives = validated_data.pop('name_narratives', [])
        description_narratives = validated_data.pop('description_narratives', [])
        activity_description_narratives = validated_data.pop('activity_description_narratives', [])

        instance = iati_models.Location.objects.create(**validated_data)

        location_name = iati_models.LocationName.objects.create(location=instance)
        location_description = iati_models.LocationDescription.objects.create(location=instance)
        location_activity_description = iati_models.LocationActivityDescription.objects.create(location=instance)

        save_narratives(location_name, name_narratives, activity)
        save_narratives(location_description, description_narratives, activity)
        save_narratives(location_activity_description, activity_description_narratives, activity)

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        name_narratives = validated_data.pop('name_narratives', [])
        description_narratives = validated_data.pop('description_narratives', [])
        activity_description_narratives = validated_data.pop('activity_description_narratives', [])

        update_instance = iati_models.Location(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        location_name = iati_models.LocationName.objects.get(location=instance)
        location_description = iati_models.LocationDescription.objects.get(location=instance)
        location_activity_description = iati_models.LocationActivityDescription.objects.get(location=instance)

        save_narratives(location_name, name_narratives, activity)
        save_narratives(location_description, description_narratives, activity)
        save_narratives(location_activity_description, activity_description_narratives, activity)

        return update_instance

    class Meta:
        model = iati_models.Location
        fields = (
            'id',
            'activity',
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


class ActivityAggregationContainerSerializer(DynamicFieldsSerializer):
    activity = ActivityAggregationSerializer(source='activity_aggregation')
    children = ActivityAggregationSerializer(source='child_aggregation')
    activity_children = ActivityAggregationSerializer(source='activity_plus_child_aggregation')


class ActivitySerializer(NestedWriteMixin, DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail', read_only=True)

    id = serializers.CharField(required=False)
    iati_identifier = serializers.CharField()
    reporting_organisations = ReportingOrganisationSerializer(
        many=True,
        read_only=True,
    )
    title = TitleSerializer(required=False)

    descriptions = DescriptionSerializer(
        many=True, 
        source='description_set',
        read_only=True,
    )
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True,
        read_only=True,
    )

    # TODO ; add other-identifier serializer
    # other_identifier = serializers.OtherIdentifierSerializer(many=True,source="?")

    activity_status = CodelistSerializer(required=False)
    activity_dates = ActivityDateSerializer(
        many=True,
        source='activitydate_set',
        read_only=True,
        required=False,
        )

    # TODO ; add contact-info serializer
    # note; contact info has a sequence we should use in the ContactInfoSerializer!
    contact_info = ContactInfoSerializer(
            many=True, 
            source="contactinfo_set",
            read_only=True,
            required=False,
            )

    activity_scope = CodelistSerializer(source='scope', required=False)
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set',
        read_only=True,
        required=False,
        )
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activityrecipientregion_set',
        read_only=True,
        required=False,
        )
    locations = LocationSerializer(
            many=True, 
            source='location_set',
            read_only=True,
            required=False,
            )
    sectors = ActivitySectorSerializer(
        many=True,
        source='activitysector_set',
        read_only=True,
        required=False,
        )

    # TODO ; add country-budget-items serializer
    # country_budget_items = serializers.CountryBudgetItemsSerializer(many=True,source="?")

    humanitarian_scope = HumanitarianScopeSerializer(
            many=True, 
            source='humanitarianscope_set',
            read_only=True,
            required=False,
            )

    policy_markers = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set',
        read_only=True,
        required=False,
        )

    collaboration_type = CodelistSerializer(required=False)
    default_flow_type = CodelistSerializer(required=False)
    default_finance_type = CodelistSerializer(required=False)
    default_aid_type = CodelistSerializer(required=False)
    default_tied_status = CodelistSerializer(required=False)

    budgets = BudgetSerializer(
            many=True, 
            source='budget_set',
            read_only=True,
            )

    # note; planned-disbursement has a sequence in PlannedDisbursementSerializer
    planned_disbursements = PlannedDisbursementSerializer(
            many=True, 
            source='planneddisbursement_set',
            read_only=True,
            )

    capital_spend = CapitalSpendSerializer(required=False)

    transactions = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='activities:activity-transactions',
        )
    # transactions = TransactionSerializer(
    #     many=True,
    #     source='transaction_set')

    document_links = DocumentLinkSerializer(
        many=True,
        read_only=True,
        source='documentlink_set')
    related_activities = RelatedActivitySerializer(
        many=True, 
        read_only=True,
        source='relatedactivity_set')

    # TODO ; add legacy-data serializer? note: we dont parse legacy data atm.
    # legacy_data = LegacyDataSerializer(many=True, source="?")

    # TODO ; add conditions serializer
    # conditions = serializers.ConditionsSerializer(many=True,source="?")

    results = ResultSerializer(
            many=True, 
            read_only=True,
            source="result_set")
    
    # TODO ; add crs-add serializer
    # note; crs-add has a sequence in CrsAddSerializer
    # crs_add = serializers.CrsAddSerializer(many=True, source="?")

    # TODO ; add fss serializer
    # fss = serializers.FssSerializer(many=True, source="?") 
    
    # activity attributes
    last_updated_datetime = serializers.DateTimeField(required=False)
    xml_lang = serializers.CharField(source='default_lang', required=False)
    default_currency = CodelistSerializer(required=False)

    humanitarian = serializers.BooleanField(required=False)

    # other added data
    aggregations = ActivityAggregationContainerSerializer(source="*", read_only=True)

    def validate(self, data):
        validated = validators.activity(
            data.get('iati_identifier'),
            data.get('default_lang'),
            data.get('hierarchy'),
            data.get('humanitarian'),
            data.get('last_updated_datetime'),
            data.get('linked_data_uri'),
            data.get('default_currency'),
            data.get('dataset'),
            data.get('activity_status', {}).get('code'),
            data.get('scope', {}).get('code'),
            data.get('collaboration_type', {}).get('code'),
            data.get('default_flow_type', {}).get('code'),
            data.get('default_finance_type', {}).get('code'),
            data.get('default_aid_type', {}).get('code'),
            data.get('default_tied_status', {}).get('code'),
            data.get('planned_start'),
            data.get('actual_start'),
            data.get('start_date'),
            data.get('planned_end'),
            data.get('actual_end'),
            data.get('end_date'),
            data.get('title', {})
        )

        return handle_errors(validated)

    def create(self, validated_data):
        title_data = validated_data.pop('title', None)
        title_narratives_data = validated_data.pop('title_narratives', None)
        activity_status = validated_data.pop('activity_status', None)
        activity_scope = validated_data.pop('activity_scope', None)
        collaboration_type = validated_data.pop('collaboration_type', None)
        default_flow_type = validated_data.pop('default_flow_type', None)
        default_finance_type = validated_data.pop('default_finance_type', None)
        default_aid_type = validated_data.pop('default_aid_type', None)
        default_tied_status = validated_data.pop('default_tied_status', None)

        instance = iati_models.Activity(**validated_data)

        instance.activity_status = activity_status
        instance.scope = activity_scope
        instance.collaboration_type = collaboration_type
        instance.default_flow_type = default_flow_type
        instance.default_finance_type = default_finance_type
        instance.default_aid_type = default_aid_type
        instance.default_tied_status = default_tied_status

        instance.save()

        if title_data:
            title = iati_models.Title.objects.create(**title_data)
            instance.title = title

            if title_narratives_data:
                save_narratives(title, title_narratives_data, instance)

        return instance


    def update(self, instance, validated_data):
        title_data = validated_data.pop('title', None)
        title_narratives_data = validated_data.pop('title_narratives', None)
        activity_status = validated_data.pop('activity_status', None)
        activity_scope = validated_data.pop('activity_scope', None)
        collaboration_type = validated_data.pop('collaboration_type', None)
        default_flow_type = validated_data.pop('default_flow_type', None)
        default_finance_type = validated_data.pop('default_finance_type', None)
        default_aid_type = validated_data.pop('default_aid_type', None)
        default_tied_status = validated_data.pop('default_tied_status', None)

        update_instance = iati_models.Activity(**validated_data)
        update_instance.id = instance.id

        if title_data:
            title = iati_models.Title.objects.create(**title_data)
            instance.title = title

        update_instance.activity_status = activity_status
        update_instance.scope = activity_scope
        update_instance.collaboration_type = collaboration_type
        update_instance.default_flow_type = default_flow_type
        update_instance.default_finance_type = default_finance_type
        update_instance.default_aid_type = default_aid_type
        update_instance.default_tied_status = default_tied_status

        update_instance.save()

        if title_narratives_data:
            save_narratives(title, title_narratives_data, instance)

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
            'dataset',
        )


# class CheckValidIATIMixin():

#     def save(self, *args, **kwargs):
#         instance = super(CheckValidIATIMixin, self).save(*args, **kwargs)

#         # query activity and check if it is valid or not

#         activity = instance.activity

#         if (activity.is_valid_iati)

#         activity.is_valid_iati = True
#         activity.save()

#         # check if activity has the required fields set


#CRUD Serializers

class SectorCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_codelists_models.Sector
        fields = '__all__'


class ActivityCrudSerializer(serializers.ModelSerializer):
    sectors = SectorCrudSerializer(many=True)

    def create(self, validated_data):
        sectors = validated_data.pop('sectors')
        activity = iati_models.Activity.objects.create(**validated_data)
        if sectors: # Bombs without this check
            iati_models.Sector.objects.create(activity=activity, **sectors)  # Errors here
        return activity
    class Meta:
        model = iati_models.Activity
        fields = (
            'id',
            'sectors',
        )


class ActivitySectorCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.ActivitySector
        fields = (
            #'id',
            'sector',
            #'percentage',
            #'vocabulary',
            #'vocabulary_uri',
        )

        
class SectorCrudAssociateSerializer(serializers.ModelSerializer):
    sectors = ActivitySectorCrudSerializer(many=True, required=False)
    
    def create(self, validated_data):
        sectors_data = validated_data.pop('sectors')
        activity = iati_models.Activity.objects.create(**validated_data)
        for sector in sectors_data:
            d=dict(sector)
            iati_models.ActivitySector.objects.create(activity=activity, sector=d['sector'])
        return activity

    def update(self, instance, validated_data):
        sectors_data = validated_data.pop('sectors')
        for item in validated_data:
            if iati_models.Activity._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        iati_models.ActivitySector.objects.filter(activity=instance).delete()
        for sector in sectors_data:
            d=dict(sector)
            iati_models.ActivitySector.objects.create(activity=instance, sector=d['sector'])
        instance.save()
        return instance
    class Meta:
        model = iati_models.Activity
        fields = (
            'id',
            'sectors',
            'sector',
            )
    
    class Meta:
        model = iati_models.Activity
        fields = (
            'id',
            'sectors',
            'sector',
            )
