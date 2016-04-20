from factory.django import DjangoModelFactory
from factory import SubFactory
from iati_synchroniser.models import IatiXmlSource
from iati_synchroniser.models import Publisher
from datetime import datetime


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class PublisherFactory(NoDatabaseFactory):
    class Meta:
        model = Publisher

    org_id = 'NL-1'
    org_abbreviate = 'Minbuza'
    org_name = 'Ministry of Foreign Affairs (Netherlands)'


class DatasetFactory(NoDatabaseFactory):
    class Meta:
        model = IatiXmlSource

    ref = 'nl-1'
    title = '1998-2008 Activities'
    type = 1
    publisher = SubFactory(PublisherFactory)
    source_url = 'http://nourl.com/NL-1.xml'
    date_created = datetime(2016, 1, 1)
    date_updated = datetime(2016, 1, 2)
    last_found_in_registry = datetime(2016, 1, 3)
    iati_standard_version = '2.02'
    is_parsed = True
    added_manually = False