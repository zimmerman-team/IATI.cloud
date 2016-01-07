"""
    Unit tests and integration tests for parser.
"""

from django.core import management
from iati.factory import iati_factory
from unittest import skip
from django.test import TestCase as DjangoTestCase # Runs each test in a transaction and flushes database

import iati_codelists.models as codelist_models
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.parser.genericXmlParser import XMLParser as GenericParser


# TODO: use factories instead of these fixtures
def setUpModule():
    fixtures = ['test_codelists.json', 'test_vocabulary',]

    for fixture in fixtures:
        management.call_command("loaddata", fixture)


def tearDownModule():
    management.call_command('flush', interactive=False, verbosity=0)


# TODO: refactor in test util module
def build_activity(version="2.01", *args, **kwargs):
    activity = iati_factory.ActivityFactory.build(
        iati_standard_version=codelist_models.Version.objects.get(code=version), # requires Version codelist
        *args,
        **kwargs
    )
    return activity


class GenericParserTestCase(DjangoTestCase):
    """
    Unit tests for the generic parser
    """

    def setUp(self):
        self.parser = GenericParser(None)

    def test_register_model_stores_model(self):
        activity = build_activity()
        self.parser.register_model('Activity', activity)
        self.assertTrue(self.parser.model_store['Activity'][0] == activity)

    def test_register_model_stores_model_by_name(self):
        # TODO: put this all under genericparser
        parser = Parser_201(None)
        
        activity = build_activity()
        parser.register_model(activity)
        self.assertTrue(parser.model_store['Activity'][0] == activity)

    def test_get_model_returns_model(self):
        test_activity = build_activity()
        self.parser.model_store['Activity'] = [test_activity]

        activity = self.parser.get_model('Activity')
        self.assertTrue(activity == test_activity)

    def test_pop_model_returns_model_and_removes(self):
        test_activity = build_activity()
        self.parser.model_store['Activity'] = [test_activity]

        activity = self.parser.pop_model('Activity')
        self.assertTrue(activity == test_activity)

        with self.assertRaises(Exception):
            activity = self.parser.model_store['Activity'][0]

    @skip('NotImplemented')
    def test_save_model_saves_model(self):
        raise NotImplementedError()

    @skip('NotImplemented')
    def test_generate_function_name(self):
        """
        Test function name gets generated appropriately
        """
        raise NotImplementedError()

    @skip('NotImplemented')
    def test_save_all_models(self):
        """
        Test all models are stored in order of input
        """
        raise NotImplementedError()

class IatiParserTestCase(DjangoTestCase):
    """
    Unit tests for ParseIati()
    """
    @skip('NotImplemented')
    def test_prepare_parser(self):
        """
        Test the parser gets prepared accordingly
        """
        raise NotImplementedError()

class ParserTestCase(DjangoTestCase):
    """
    Integration tests for the parser
    """
    def setUp(self):
        pass

    @skip('NotImplemented')
    def test_parse_url_parses_test_file(self):
        """
        Test a sample activity file gets parsed accordingly 
        """
        raise NotImplementedError()

