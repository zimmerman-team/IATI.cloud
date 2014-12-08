import pytest
from django.test import RequestFactory
from iati.factory import iati_factory
from api.activity import serializers


class TestActivitySerializers:

    def test_DefaultAidTypeSerializer(self):
        aidtype = iati_factory.AidTypeFactory.build(
            code=10,
        )
        serializer = serializers.DefaultAidTypeSerializer(aidtype)
        assert serializer.data['code'] == str(aidtype.code), \
            """
            the data in aidtype.code should be serialized to a field named code
            inside the serialized object
            """

    def test_DefaultFlowTypeSerializer(self):
        flowtype = iati_factory.FlowTypeFactory.build(
            code=10,
        )
        serializer = serializers.DefaultFlowTypeSerializer(flowtype)
        assert serializer.data['code'] == flowtype.code, \
            """
            the data in flowtype.code should be serializer to a field named
            code inside the serialized object
            """

    def test_ActivityStatusSerializer(self):
        activity_status = iati_factory.ActivityStatusFactory.build(
            code=10,
        )
        serializer = serializers.ActivityStatusSerializer(activity_status)
        assert serializer.data['code'] == activity_status.code, \
            """
            the data in activity_status.code should be serialized to a field
            named code inside the serialized object
            """

    def test_CollaborationTypeSerializer(self):
        collaboration_type = iati_factory.CollaborationTypeFactory.build(
            code=1,
        )
        serializer = serializers.CollaborationTypeSerializer(
            collaboration_type)
        assert serializer.data['code'] == collaboration_type.code, \
            """
            the data in collaboration_type.code should be serialized to a field
            named code inside the serialized object
            """

    def test_TotalBudgetSerializer(self):
        activity = iati_factory.ActivityFactory.build(
            total_budget=1000,
            total_budget_currency=iati_factory.CurrencyFactory.build(
                code='USD')
        )
        serializer = serializers.TotalBudgetSerializer(activity)
        assert serializer.data['value'] == activity.total_budget, \
            """
            activity.total_budget should be serialized to a field called value
            inside the serialized object
            """
        assert serializer.data['currency'] == \
            activity.total_budget_currency.code, \
            """
            activity.total_budget.code should be serialized to a field called
            currency inside the serialized object
            """

    def test_BudgetSerializer(self):
        budget = iati_factory.BudgetFactory.build(
            type_id=1,
            period_start='2014-12-1',
            period_end='2014-12-2',
        )
        serializer = serializers.BudgetSerializer(budget)
        assert serializer.data['type'] == budget.type_id, \
            """
            budget.type_id should be serialized to a field called 'type' inside
            the serializer object
            """
        assert serializer.data['period_start'] == budget.period_start, \
            """
            budget.period_start should be serialized to a field called
            period_start in the serialized object
            """
        assert serializer.data['period_end'] == budget.period_end, \
            """
            budget.period_end should be serialized to a field called
            period_end in the serialized object
            """
        assert 'value' in serializer.data, \
            """
            a serialized budget should contain an object called value
            """

    def test_ValueSerializer(self):
        budget = iati_factory.BudgetFactory.build(
            value=100,
            value_date='2014-12-1',
            currency=iati_factory.CurrencyFactory.build(code='USD')
        )
        serializer = serializers.BudgetSerializer.ValueSerializer(budget)
        assert serializer.data['value'] == budget.value, \
            """
            budget.value should be serialized to a field called value
            by the ValueSerializer
            """
        assert serializer.data['date'] == budget.value_date, \
            """
            budget.value_date should be serialized to  field called
            date by the ValueSerialized
            """
        assert serializer.data['currency'] == 'USD', \
            """
            budget.currency.code should be serialized to a field called
            currency by the ValueSerializer
            """

    def test_ActivityDateSerializer(self):
        activity = iati_factory.ActivityFactory.build(
            start_planned='2014-12-1',
            end_planned='2014-12-2',
            start_actual='2014-12-3',
            end_actual='2014-12-4',
        )
        serializer = serializers.ActivityDateSerializer(activity)
        assert serializer.data['start_planned'] == '2014-12-1', \
            """
            activity.start_planned should be serialized to a field called
            start_planned by the ActivityDateSerializer
            """
        assert serializer.data['end_planned'] == '2014-12-2', \
            """
            activity.end_planned should be serialized to a field called
            end_planned by the ActivityDateSerializer
            """
        assert serializer.data['start_actual'] == '2014-12-3', \
            """
            activity.start_actual should be serialized to a field called
            start_actual by the ActivityDateSerializer
            """
        assert serializer.data['end_actual'] == '2014-12-4', \
            """
            activity.end_actual should be serialized to a field called
            end_actual by the ActivityDateSerializer
            """

    @pytest.mark.django_db
    def test_ReportingOrganisationSerializer(self):
        request_dummy = RequestFactory().get('/')
        organisation = iati_factory.OrganisationFactory.build()
        activity = iati_factory.ActivityFactory.build(
            secondary_publisher=True,
            reporting_organisation=organisation,
        )
        data = serializers.ReportingOrganisationSerializer(
            activity,
            context={'request': request_dummy}
        ).data
        assert data['secondary_reporter'] == activity.secondary_publisher,\
            """
            activity.secondary_publisher should be serialized to a field
            called 'secondary_reporter' by the ReportingOrganisationSerializer
            """
        assert 'organisation' in data, \
            """
            serializer.data should contain an object called 'organisation'
            """
        assert 'code' and 'name' and 'type' in data['organisation'], \
            """
            The organisation serialized by the ReportingOrganisationSerializer
            should atleast contain the fields 'code', 'name', and 'type'
            """

    def test_ActivityPolicyMarkerSerializer(self):
        policy_marker = iati_factory.ActivityPolicyMarkerFactory.build(
            alt_policy_marker='alt_policy_marker',
        )
        data = serializers.ActivityPolicyMarkerSerializer(policy_marker).data
        assert data['narative'] == policy_marker.alt_policy_marker,\
            """
            policy_marker.alt_policy_marker should be serialized to a field
            called 'narative'
            """
        assert 'vocabulary' in data,\
            'serializer.data should contain an object called vocabulary'
        assert 'significance' in data,\
            'serializer.data should contain an object called significance'
        assert 'code' in data,\
            'serializer.data should contain an object called code'

    def test_PolicyMarkerSerializer(self):
        policy_marker = iati_factory.PolicyMarkerFactory.build(code=1)
        serializer = serializers.ActivityPolicyMarkerSerializer.\
            PolicyMarkerSerializer(policy_marker)
        assert serializer.data['code'] == policy_marker.code,\
            "policy_marker.code should be serialized to a field called 'code'"

    def test_VocabularySerializer(self):
        vocabulary = iati_factory.VocabularyFactory.build(code=1)
        serializer = serializers.ActivityPolicyMarkerSerializer.\
            VocabularySerializer(vocabulary)
        assert serializer.data['code'] == str(vocabulary.code),\
            "vocabulary.code should be serialized to a field called 'code'"

    def test_PolicySignificanceSerializer(self):
        significance = iati_factory.PolicySignificanceFactory.build(code=1)
        serializer = serializers.ActivityPolicyMarkerSerializer.\
            PolicySignificanceSerializer(significance)
        assert serializer.data['code'] == significance.code,\
            "significance.code should be serialized to a field called 'code'"

    def test_TitleSerializer(self):
        activity = iati_factory.ActivityFactory.build(id=None)
        serializer = serializers.TitleSerializer(activity)
        assert 'narratives' in serializer.data,\
            "A serialized title should containt a object 'narratives'"

    def test_TitleNarrativesSerializer(self):
        title = iati_factory.TitleFactory.build(
            title='activity title',
            language=iati_factory.LanguageFactory.build(code='fr')
        )
        serializer = serializers.TitleSerializer.NarrativeSerializer(title)
        assert serializer.data['text'] == title.title,\
            "'title.title' should be serialized to a field called 'text'"
        assert serializer.data['language'] == title.language.code,\
            """
            'title.language' should be serialized to a field called 'language'
            """

    def test_DescriptionSerializer(self):
        description = iati_factory.DescriptionFactory.build(
            type=iati_factory.DescriptionTypeFactory.build(code=1)
        )
        serializer = serializers.DescriptionSerializer(description)
        assert serializer.data['type'] == description.type.code,\
            """
            'description.type.code' should be serialized to a field called
            'type'
            """

    def test_DescriptionNarrativeSerializer(seslf):
        description = iati_factory.DescriptionFactory.build(
            description='some text to describe an activity',
            language=iati_factory.LanguageFactory.build(code='fr'),
        )
        serializer = serializers.DescriptionSerializer.NarrativeSerializer(
            description)
        assert serializer.data['language'] == description.language.code,\
            """
            'description.language' should be serialized to a field called
            'language'
            """
        assert serializer.data['text'] == description.description,\
            """
            'description.description' should be serialid to a field called
            'text'
            """

    def test_ActivitySerializerDynamicFields(self):
        activity = iati_factory.ActivityFactory.build(
            id='identifier',
            iati_identifier='iati-identifier'
        )
        fields = ['id']
        serializer = serializers.ActivitySerializer(activity, fields=fields)
        assert serializer.data['id'] == 'identifier', \
            """
            activity.id should be serialized since it is specified with
            the fields parameter
            """
        assert 'iati_identifier' not in serializer.data, \
            """
            activity.iati_identifier should NOT be serialized since it is
            not specified in the fields parameter
            """
