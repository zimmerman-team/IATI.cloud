"""
    Unit tests and integration tests for parser.
"""
from unittest import skip

import pytest
from django.core import management
from django.test import TestCase as DjangoTestCase
from lxml.builder import E

import iati_codelists.models as codelist_models
from iati.factory import iati_factory
from iati.models import Activity
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.parser.iati_parser import IatiParser

# TODO: use factories instead of these fixtures


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        fixtures = ['test_vocabulary', 'test_codelists.json', ]

        for fixture in fixtures:
            management.call_command("loaddata", fixture)


def tearDownModule():
    pass


# TODO: refactor in test util module
def build_activity(version="2.01", *args, **kwargs):
    activity = iati_factory.ActivityFactory.build(
        iati_standard_version=codelist_models.Version.objects.get(
            code=version),  # requires Version codelist
        *args,
        **kwargs
    )
    return activity


class IatiParserTestCase(DjangoTestCase):
    """
    Unit tests for the iati parser
    """

    def setUp(self):
        self.parser = IatiParser(None)

    def test_get_or_none_charset_encoding(self):
        self.assertIsNone(self.parser.get_or_none(
            Activity, code=u'Default-aid-type: [code="D02"\xa0]\xa0'))
        self.assertIsNone(self.parser.get_or_none(Activity, code=u'\xa0'))
        self.assertIsNone(self.parser.get_or_none(
            codelist_models.AidType, code=u''))
        self.assertIsNone(self.parser.get_or_none(
            codelist_models.AidType, code=''))

    def test_register_model_stores_model(self):
        activity = build_activity()
        self.parser.register_model('Activity', activity)
        self.assertTrue(self.parser.model_store['Activity'][0] == activity)

    def test_register_model_stores_model_by_name(self):
        parser = Parser_201(None)

        activity = build_activity()
        parser.register_model(activity, activity)
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

    def test_normalize(self):
        """
        normalize should remove spaces / tabs etc, replace special characters
        by a -
        """
        self.assertEqual(self.parser._normalize("no,commas"), 'noCOMMAcommas')

    def test_validate_date(self):
        """
        date should return valid dates and return None on an invalid date
        values lower than year 1900 or higher than 2100 should be dropped
        """

        date = self.parser.validate_date('1900-01-01')
        self.assertEqual(date.year, 1900)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)

        date = self.parser.validate_date('1899-06-01')
        self.assertEqual(date, None)

        date = self.parser.validate_date('2101-01-01')
        self.assertEqual(date, None)

    def test_get_primary_name(self):
        """
        if no primary name, set
        if primary name english, set
        if primary name and not english, dont set
        """

        narrative = E('narrative', "first narrative")
        narrative.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fr"
        primary_name = self.parser.get_primary_name(narrative, "")
        self.assertEqual(primary_name, "first narrative")

        narrative = E('narrative', "new narrative")
        narrative.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        primary_name = self.parser.get_primary_name(
            narrative, "current primary name")
        self.assertEqual(primary_name, "new narrative")

        narrative = E('narrative', "french narrative")
        narrative.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fr"
        primary_name = self.parser.get_primary_name(narrative, primary_name)
        self.assertEqual(primary_name, "new narrative")

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
