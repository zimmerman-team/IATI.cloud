# TODO: no need to test codelist fields separately; instead test the whole
# serializer in once along with the code and vocabulary fields. Or is
# testing the fields separately preferable?

# Runs each test in a transaction and flushes database
from django.test import RequestFactory, TestCase

from api.activity.serializers import LocationSerializer
from iati.factory import iati_factory


# TODO: separate into several test cases
class LocationSerializerTestCase(TestCase):

    request_dummy = RequestFactory().get('/')
    request_dummy.query_params = dict()

    def test_locationSerializer(self):

        location = iati_factory.LocationFactory.build()

        serializer = LocationSerializer(
            location, context={'request': self.request_dummy})

        assert serializer.data['ref'] == location.ref,\
            """
            a serialized location should contain a field 'ref' that contains
            the data in location.ref
            """

        assert 'location_reach' in serializer.data,\
            """
            a serialized location should contain a field 'location_reach'
            """

        assert 'point' in serializer.data,\
            """
            a serialized location should contain a field 'point'
            """

        assert 'exactness' in serializer.data,\
            """
            a serialized location should contain a field 'exactness'
            """

        assert 'location_class' in serializer.data,\
            """
            a serialized location should contain a field 'location_class'
            """

        assert 'feature_designation' in serializer.data,\
            """
            a serialized location should contain a field 'feature_designation'
            """
