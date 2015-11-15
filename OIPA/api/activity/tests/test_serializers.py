# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory
from iati.factory import iati_factory
from api.activity import serializers

class CodelistSerializerTestCase(TestCase):
    def test_codelist_serializer(self):
        version = iati_factory.VersionFactory.build()
        serializer = serializers.CodelistSerializer(version)

        assert serializer.data['code'] == version.code,\
            """
            'codelist.code' should be serialized to a field called 'code'
            """
        assert serializer.data['name'] == version.name,\
            """
            'codelist.name' should be serialized to a field called 'name'
            """

class NarrativeSerializerTestCase(TestCase):

    def test_narrative_serializer(self):
        narrative = iati_factory.NarrativeFactory.build()
        serializer = serializers.NarrativeSerializer(narrative)

        assert serializer.data['text'] == narrative.content,\
            """
            'narrative.content' should be serialized to a field called 'text'
            """
        assert serializer.data['language']['code'] == narrative.language.code,\
            """
            'narrative.language' should be serialized to a field called 'language'
            """


# TODO: separate into several test cases
class ActivitySerializerTestCase(TestCase):

    request_dummy = RequestFactory().get('/')

    def test_DocumentLinkSerializer(self):
        doc_link = iati_factory.DocumentLinkFactory.create()
        intermediate = iati_factory.DocumentLinkCategoryFactory.build(document_link=doc_link)
        serializer = serializers.DocumentLinkSerializer(doc_link)
        assert serializer.data['url'] == doc_link.url,\
            """
            'document_link.url' should be serialized to a field called 'url'
            """
        assert 'format' and 'category' and 'title' in serializer.data,\
            """
            a serialized document_link should also contain the fields 'format'
            'category' and 'title'
            """

        assert type(serializer.fields['format']) is serializers.CodelistSerializer,\
            """
            the field 'format' should be a CodelistSerializer
            """

        assert type(serializer.fields['categories'].child) is serializers.\
            DocumentLinkSerializer.DocumentCategorySerializer,\
            """
            the field 'categories' should be a DocumentCategorySerializer
            """

        assert type(serializer.fields['title'].child) is serializers.\
            NarrativeContainerSerializer,\
            """
            the field 'title' should be a TitleSerializer
            """

    def test_FileFormatSerializer(self):
        file_format = iati_factory.FileFormatFactory.build()
        serializer = serializers.CodelistSerializer(
            file_format)
        assert serializer.data['code'] == file_format.code,\
            """
            'file_format.code' should be serialized to a field called 'code'
            """

    def test_DocumentCategorySerializer(self):

        doc_category = iati_factory.DocumentCategoryFactory.build()
        serializer = serializers.DocumentLinkSerializer\
            .DocumentCategorySerializer(doc_category)

        assert serializer.data['code'] == doc_category.code,\
            """
            'document_category.code' should be serialized to a field called
            'code'
            """

    def test_DocumentTitleSerializer(self):
        title = iati_factory.DocumentLinkTitleFactory.build()
        iati_factory.NarrativeFactory.create(related_object=title, content="title")
        serializer = serializers.NarrativeContainerSerializer(title)
        assert serializer.data['narratives'][0]['text'] == "title",\
            """
            'title' should be serialized as 'title.narratives.text'
            """

    def test_aid_type_serializer(self):
        aidtype = iati_factory.AidTypeFactory.build(
            code='10',
        )
        serializer = serializers.CodelistSerializer(aidtype)
        assert serializer.data['code'] == aidtype.code, \
            """
            the data in aidtype.code should be serialized to a field named code
            inside the serialized object
            """

    def test_flow_type_serializer(self):
        flowtype = iati_factory.FlowTypeFactory.build(
            code='10',
        )
        serializer = serializers.CodelistSerializer(flowtype)
        assert serializer.data['code'] == flowtype.code, \
            """
            the data in flowtype.code should be serializer to a field named
            code inside the serialized object
            """

    def test_ActivityStatusSerializer(self):
        activity_status = iati_factory.ActivityStatusFactory.build(
            code='10',
        )
        serializer = serializers.CodelistSerializer(activity_status)
        assert serializer.data['code'] == activity_status.code, \
            """
            the data in activity_status.code should be serialized to a field
            named code inside the serialized object
            """

    def test_CollaborationTypeSerializer(self):
        collaboration_type = iati_factory.CollaborationTypeFactory.build(
            code='1',
        )
        serializer = serializers.CodelistSerializer(
            collaboration_type)
        assert serializer.data['code'] == collaboration_type.code, \
            """
            the data in collaboration_type.code should be serialized to a field
            named code inside the serialized object
            """

    def test_BudgetSerializer(self):
        budget = iati_factory.BudgetFactory.build(
            period_start='2014-12-01',
            period_end='2014-12-02',
        )
        serializer = serializers.BudgetSerializer(budget)
        assert 'type' in serializer.data,\
            """
            a serialized budget should contain a field called 'type'
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

    def test_BudgetTypeSerializer(self):
        budget_type = iati_factory.BudgetTypeFactory.build(code='1')
        serializer = serializers.CodelistSerializer(
            budget_type)
        assert serializer.data['code'] == budget_type.code,\
            """
            'budget_type.code' should be serialized to a vield callded 'code'
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
        assert 'currency' in serializer.data,\
            """
            a serialized value should contain an object valled 'currency'
            """

    def test_ActivityDateSerializer(self):
        date_type = iati_factory.ActivityDateFactory.create()
        serializer = serializers.ActivityDateSerializer(date_type)

        self.assertTrue('iso_date' in serializer.data)
        self.assertTrue(type(serializer.fields['type']) is serializers.CodelistSerializer)

    def test_ActivityDateTypeSerializer(self):
        activity_date_type = iati_factory.ActivityDateTypeFactory.build(code='1')
        serializer = serializers.CodelistSerializer(
            activity_date_type)
        assert serializer.data['code'] == activity_date_type.code,\
            """
            'activity_date_type.code' should be serialized to a vield callded 'code'
            """

    def test_ReportingOrganisationSerializer(self):
        reporting_organisation = iati_factory.ReportingOrganisationFactory.build()

        data = serializers.ReportingOrganisationSerializer(
            reporting_organisation
            ).data
        assert data['secondary_reporter'] == reporting_organisation.secondary_reporter,\
            """
            reporting_organisation.seconary_reporter should be serialized to a field
            called 'secondary_reporter' by the ReportingOrganisationSerializer
            """
        # assert 'organisation' in data, \
        #     """
        #     serializer.data should contain an object called 'organisation'
        #     """
        assert 'ref' and 'type' in data, \
            """
            The organisation serialized by the ReportingOrganisationSerializer
            should atleast contain the fields 'code', 'name', and 'type'
            """

    def test_OrganisationTypeSerializer(self):
        org_type = iati_factory.OrganisationTypeFactory.build()
        serializer = serializers.CodelistSerializer(org_type)
        self.assertTrue(serializer.data['code'] == org_type.code)

    def test_ActivityPolicyMarkerSerializer(self):
        policy_marker = iati_factory.ActivityPolicyMarkerFactory.build()
        data = serializers.ActivityPolicyMarkerSerializer(policy_marker).data

        assert 'narratives' in data
        assert 'vocabulary' in data,\
            'serializer.data should contain an object called vocabulary'
        assert 'significance' in data,\
            'serializer.data should contain an object called significance'
        assert 'code' in data,\
            'serializer.data should contain an object called code'

    def test_PolicyMarkerSerializer(self):
        policy_marker = iati_factory.PolicyMarkerFactory.build()
        serializer = serializers.CodelistSerializer(policy_marker)
        assert serializer.data['code'] == policy_marker.code,\
            "policy_marker.code should be serialized to a field called 'code'"

    def test_PolicySignificanceSerializer(self):
        significance = iati_factory.PolicySignificanceFactory.build()
        serializer = serializers.CodelistSerializer(significance)
        assert serializer.data['code'] == significance.code,\
            "significance.code should be serialized to a field called 'code'"

    def test_TitleSerializer(self):
        title = iati_factory.TitleFactory.build()
        iati_factory.NarrativeFactory.create(related_object=title, content="title")
        serializer = serializers.TitleSerializer(title)
        assert serializer.data['narratives'][0]['text'] == "title",\
            """
            'title' should be serialized as 'title.narratives.text'
            """

    def test_DescriptionSerializer(self):
        description = iati_factory.DescriptionFactory.build()
        iati_factory.NarrativeFactory.create(related_object=description, content="description")
        serializer = serializers.DescriptionSerializer(description)
        assert serializer.data['narratives'][0]['text'] == "description",\
            """
            'description' should be serialized as 'description.narratives.text'
            """
        assert 'type' in serializer.data,\
            """
            a serialized description should contain the fields 'type' and 'narratives'
            """

    def test_DescriptionTypeSerializer(self):
        description_type = iati_factory.DescriptionTypeFactory.build()
        serializer = serializers.CodelistSerializer(description_type)
        assert serializer.data['code'] == description_type.code,\
            """
            'description_type.code' should be serialized to a field called
            'code'
            """

    def test_ActivitySerializerDynamicFields(self):
        activity = iati_factory.ActivityFactory.build(
            id='identifier',
            iati_identifier='iati-identifier'
        )
        fields = ('id',)
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

    def test_ActivitySectorSerializer(self):
        activity_sector = iati_factory.ActivitySectorFactory.build(
            percentage=80
        )
        serializer = serializers.ActivitySectorSerializer(
            activity_sector,
            context={'request': self.request_dummy},
        )
        assert serializer.data['percentage'] == activity_sector.percentage,\
            """
            'activity_sector.percentage' should be serialized to a field
            called percentage
            """
        assert 'sector' and 'vocabulary' in serializer.data,\
            """
            a serialized ActivitySector should contain the objects 'sector'
            and 'vocabulary'
            """
        assert 'url' and 'code' and 'name' in serializer.data['sector'],\
            """
            the serialized sector should contain the fields 'url, 'code', and
            'name'
            """
    def test_SectorVocabularySerializer(self):
        vocabulary = iati_factory.SectorVocabularyFactory.build()
        serializer = serializers.CodelistSerializer(vocabulary)
        assert serializer.data['code'] == vocabulary.code,\
            """
            'vocabulary.code' should be serialized to a field called 'code'
            """

    def test_ActivityRecipientRegionSerializer(self):
        recipient_region = iati_factory.ActivityRecipientRegionFactory.build()
        serializer = serializers.ActivityRecipientRegionSerializer(recipient_region, 
            context={'request': self.request_dummy}
        )

        assert serializer.data['percentage'] == recipient_region.percentage,\
            """
            'recipient_region.percentage' should be serialized to a field
            called 'percentage'
            """
        assert 'region' and 'vocabulary' in serializer.data,\
            """
            a serialized RecipientRegion should contain the fields 'region'
            and 'vocabulary'
            """
        assert 'url' and 'code' and 'name' in serializer.data['region'],\
            """
            a region, serialized by the ActivityRecipientRegionSerializer
            should contain the fields 'url', 'code' and 'name'
            """

    def test_ParticipatingOrganisationSerializer(self):
        part_org = iati_factory.ParticipatingOrganisationFactory.build()
        serializer = serializers.ParticipatingOrganisationSerializer(
            part_org,
            context={'request': self.request_dummy}
        )
        assert 'role' and 'type' and 'ref' and 'narratives' in serializer.data,\
            """
            a serialized ParticipatingOrganisation should contain the fields
            'organisation' and 'role'
            """

    def test_OrganisationRoleSerializer(self):
        role = iati_factory.OrganisationRoleFactory.build()
        serializer = serializers.CodelistSerializer(role)
        assert serializer.data['code'] == role.code,\
            """
            'role.code' should be serialized to a field called 'code'
            """

    def test_RecipientCountrySerializer(self):
        recipient_country = iati_factory.RecipientCountryFactory.build(
            percentage=80
        )
        serializer = serializers.RecipientCountrySerializer(
            recipient_country,
            context={'request': self.request_dummy}
        )
        assert serializer.data['percentage'] == recipient_country.percentage,\
            """
            'recipient_country.percentage' should be serialized to a field
            called 'percentage'
            """
        assert 'country' in serializer.data,\
            """
            a serialized RecipientCountry should contain the field 'country'
            """
        assert 'url' and 'code' and 'name' in serializer.data['country'],\
            """
            the serialized country should contain the fields 'url', 'code' and
            'name'
            """

    def test_ActivityScopeSerializer(self):
        activity_scope = iati_factory.ActivityScopeFactory.build()
        serializer = serializers.CodelistSerializer(activity_scope)
        assert serializer.data['code'] == activity_scope.code,\
            """
            'activity_scope.code' should be serialized to a field called
            'code'
            """

    def test_CurrencySerializer(self):
        currency = iati_factory.CurrencyFactory.build(code='EUR')
        serializer = serializers.CodelistSerializer(currency)
        assert serializer.data['code'] == currency.code,\
            """
            'currency.code' should be serialized to a field called
            'code'
            """

    def test_FinanceTypeSerializer(self):
        finance_type = iati_factory.FinanceTypeFactory.build(code='110')
        serializer = serializers.CodelistSerializer(finance_type)
        assert serializer.data['code'] == finance_type.code,\
            """
            'finance_type.code' should be serialized to a field called
            'code'
            """

    def test_TiedStatusSerializer(self):
        tied_status = iati_factory.TiedStatusFactory.build(code='3')
        serializer = serializers.CodelistSerializer(tied_status)
        assert serializer.data['code'] == tied_status.code,\
            """
            'tied_status.code' should be serialized to a field called
            'code'
            """

    def test_CapitalSpendSerializer(self):
        activity = iati_factory.ActivityFactory.build(capital_spend=80)
        serializer = serializers.CapitalSpendSerializer(activity)
        assert serializer.data['percentage'] == activity.capital_spend,\
            """
            'activity.capital_spend' should be serialized to a field called
            'percentage'
            """

    def test_ResultTypeSerializer(self):
        result_type = iati_factory.ResultTypeFactory.build()
        serializer = serializers.CodelistSerializer(result_type)
        assert serializer.data['code'] == result_type.code,\
            """
            'result_type.code' should be serialized to a field called
            'code'
            """

    @skip('NotImplemented')
    def test_ResultSerializer(self):
        # TODO test after implementing in parser
        raise NotImplementedError()

        result = iati_factory.ResultFactory.build()
        serializer = serializers.ResultSerializer(result)

        assert serializer.data['title']['narratives'][0]['text'] == result.title,\
            """
            'result.title' should be serialized to a field called
            'title'
            """
        assert serializer.data['description']['narratives'][0]['text'] == result.description,\
            """
            'result.description' should be serialized to a field called
            'description'
            """
        assert serializer.data['aggregation_status'] == result.aggregation_status,\
            """
            'result.aggregation_status' should be serialized to a field called
            'aggregation_status'
            """
        assert 'result_type' in serializer.data, \
            """
            result.result_type should be serialized in result
            """

    def test_GeographicVocabularySerializer(self):
        vocabulary = iati_factory.GeographicVocabularyFactory.build()
        serializer = serializers.CodelistSerializer(vocabulary)
        assert serializer.data['code'] == vocabulary.code,\
            """
            'code' should be serialized in GeographicVocabularySerializer
            """

    def test_GeographicLocationClassSerializer(self):
        geo_location = iati_factory.GeographicLocationClassFactory.build()
        serializer = serializers.CodelistSerializer(geo_location)
        assert serializer.data['code'] == geo_location.code,\
            """
            'code' should be serialized in CodelistSerializer
            """

    def test_GeographicLocationReachSerializer(self):
        location_reach = iati_factory.GeographicLocationReachFactory.build()
        serializer = serializers.CodelistSerializer(location_reach)
        assert serializer.data['code'] == location_reach.code,\
            """
            'code' should be serialized in GeographicLocationReachSerializer
            """

    def test_GeographicExactnessSerializer(self):
        exactness = iati_factory.GeographicExactnessFactory.build()
        serializer = serializers.CodelistSerializer(exactness)

        assert serializer.data['code'] == exactness.code,\
            """
            'code' should be serialized in GeographicExactnessSerializer
            """

    def test_LocationTypeSerializer(self):
        type = iati_factory.LocationTypeFactory.build()
        serializer = serializers.CodelistCategorySerializer(type)

        assert serializer.data['code'] == type.code,\
            """
            'code' should be serialized in LocationTypeSerializer
            """

    def test_LocationIdSerializer(self):
        location = iati_factory.LocationFactory.build()
        serializer = serializers.LocationSerializer.LocationIdSerializer(location)

        assert serializer.data['code'] == location.location_id_code,\
            """
            'code' should be serialized in LocationIdSerializer
            """
        assert 'vocabulary' in serializer.data,\
            """
            LocationIdSerializer should serialize vocabulary
            """

    def test_AdministrativeSerializer(self):
        administrative = iati_factory.LocationAdministrativeFactory.build()
        serializer = serializers.LocationSerializer.AdministrativeSerializer(administrative)

        assert serializer.data['code'] == administrative.code,\
            """
            'code' should be serialized in AdministrativeSerializer
            """
        assert serializer.data['level'] == administrative.level,\
            """
            'level' should be serialized in AdministrativeSerializer
            """
        assert 'vocabulary' in serializer.data,\
            """
            AdministrativeSerializer should serialize vocabulary
            """

    def test_LocationSerializer(self):
        # TODO: test narrative models separately
        # TODO: test point serializers etc... separately

        location = iati_factory.LocationFactory.build()
        serializer = serializers.LocationSerializer(location)

        # assert serializer.data['name']['narratives'][0]['text'] == location.name,\
        #     """
        #     'name' should be serialized in location
        #     """
        # assert serializer.data['description']['narratives'][0]['text'] == location.description,\
        #     """
        #     'description' should be serialized in location
        #     """
        # assert serializer.data['activity_description']['narratives'][0]['text'] == location.activity_description,\
        #     """
        #     'activity_description' should be serialized in location
        #     """
        required_fields = (
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
        assertion_msg = "the field '{0}' should be in the serialized location"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)

    # @pytest.mark.django_db
    def test_activitySerializer(self):
        request_dummy = RequestFactory().get('/')
        request_dummy.query_params = dict()

        activity = iati_factory.ActivityFactory.build(
            last_updated_datetime=datetime.datetime.now(),
            hierarchy=1,
            linked_data_uri='www.data.example.org/123',
            xml_source_ref='www.data.example.org/123/1234.xml'
        )
        serializer = serializers.ActivitySerializer(
            activity, context={'request': request_dummy})

        assert serializer.data['id'] == activity.id,\
            """
            a serialized activity should contain a field 'id' that contains
            the data in activity.id
            """
        assert serializer.data['iati_identifier'] == activity.iati_identifier,\
            """
            a serialized activity should contain a field 'iati_identifier' that
            contains the data in activity.iati_identifier
            """

        assert serializer.data['last_updated_datetime'] ==\
            activity.last_updated_datetime.strftime("%y-%m-%d"),\
            """
            a serialized activity should contain a field 'last_updated_datetime
            that contains the data in activity.last_updated_datetime
            """
        assert serializer.data['hierarchy'] == activity.hierarchy,\
            """
            a serialized activity should contain a field 'hierarchy' that
            contains the data in activity.hierarchy
            """
        assert serializer.data['linked_data_uri'] == activity.linked_data_uri,\
            """
            a serialized activity should contain a field 'linked_data_uri'
            that contains the data in activity.linked_data_uri
            """
        assert serializer.data['xml_source_ref'] == activity.xml_source_ref,\
            """
            a serialized activity should contain a field 'xml_source_ref' that
            contains the data in activity.xml_source_ref
            """

    # @pytest.mark.django_db
    def test_activitySerializer_required_fields(self):
        request_dummy = RequestFactory().get('/')
        request_dummy.query_params = dict()

        activity = iati_factory.ActivityFactory.build()
        serializer = serializers.ActivitySerializer(
            activity, context={'request': request_dummy})

        required_fields = (
            'url',
            'id',
            'iati_identifier',
            'title',
            'description',
            'last_updated_datetime',
            'default_currency',
            'hierarchy',
            'linked_data_uri',
            'reporting_organisations',
            'participating_organisations',
            'related_activities',
            'activity_status',
            'activity_dates',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'sectors',
            'transactions',
            'policy_markers',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            'budgets',
            'capital_spend',
            'xml_source_ref',
            'document_links',
            'results',
            'locations',
            'activity_aggregations'
        )
        assertion_msg = "the field '{0}' should be in the serialized activity"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
