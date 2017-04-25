from factory.django import DjangoModelFactory
from factory import SubFactory
from iati_synchroniser.models import Dataset
from iati_synchroniser.models import Publisher
from datetime import datetime

from iati.factory.iati_factory import OrganisationFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class PublisherFactory(NoDatabaseFactory):
    class Meta:
        model = Publisher
        django_get_or_create = [ 'publisher_iati_id' ]

    organisation = SubFactory(OrganisationFactory)
    iati_id = 'NL-1'
    publisher_iati_id = 'NL-1'
    name = 'Minbuza'
    display_name = 'Ministry of Foreign Affairs (Netherlands)'

class DatasetFactory(NoDatabaseFactory):
    class Meta:
        model = Dataset

    iati_id = '31403-42090-13011-13003'
    name = 'nl-1'
    title = '1998-2008 Activities'
    filetype = 1
    publisher = SubFactory(PublisherFactory)
    source_url = 'http://nourl.com/NL-1.xml'
    date_created = datetime(2016, 1, 1)
    date_updated = datetime(2016, 1, 2)
    last_found_in_registry = datetime(2016, 1, 3)
    iati_version = '2.02'
    is_parsed = True
    added_manually = False
