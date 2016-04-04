from unittest import skip
from lxml.builder import E
from iati.models import Activity
from iati_synchroniser.factory.synchroniser_factory import DatasetFactory
from mock import MagicMock
import datetime
import iati_codelists.models as codelist_models
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.factory import iati_factory
from iati.transaction.factories import TransactionFactory
from iati.parser.genericXmlParser import XMLParser as GenericParser
from django.test import TestCase


class PostSaveActivityTestCase(TestCase):
    """
    2.01: post activity actions called
    """

    def setUp(self):
        self.parser = GenericParser(None)
        version = codelist_models.Version.objects.get(code='2.01')
        self.activity = iati_factory.ActivityFactory.create(
            id='IATI-0001',
            iati_identifier='IATI-0001',
            iati_standard_version=version,
            xml_source_ref='source_reference')

    @skip('NotImplemented')
    def test_post_save_models(self):
        """
        Check if sets related activities and activity aggregations
        """

    @skip('NotImplemented')
    def set_related_activities(self):
        """
        Check if related activities are linked to the current activity
        and the current activity is related to another activity
        """

    @skip('NotImplemented')
    def set_transaction_provider_receiver_activity(self):
        """
        Check if references to/from provider/receiver activity are set in transactions
        """

    @skip('NotImplemented')
    def set_derived_activity_dates(self):
        """
        Check if derived (actual > planned) dates are set correctly
        """

    @skip('NotImplemented')
    def test_set_activity_aggregations(self):
        """
        Check if calculated budget / transaction etc values are correct
        """

    @skip('NotImplemented')
    def test_update_activity_search_index(self):
        """
        Check if dates are set correctly
        """

    @skip('NotImplemented')
    def test_calculate_country_region_transaction_values_set_on_transaction(self):
        """
        When set on the transaction, the whole transaction will be 100% targeted to that country/region
        """

    @skip('NotImplemented')
    def test_calculate_country_region_transaction_values_not_set_on_transaction(self):
        """
        When not set on the transaction, the transaction will be targeted percentage wise.
        Percentages are given in recipient-country and/or recipient-region.
        Percentages of recipient countries and recipient regions together should add up to 100%.
        If percentages are not given, split through all countries/regions given.
        """

    @skip('NotImplemented')
    def test_calculate_sector_transaction_values_set_on_transaction(self):
        """
        When set on the transaction, the whole transaction will be 100% targeted to that sector.
        """

    @skip('NotImplemented')
    def test_calculate_sector_transaction_values_not_set_on_transaction(self):
        """
        Percentages of sectors should add up to 100%.
        If percentages are not given, split through all countries/regions given.
        """

    def test_set_country_region_transaction_with_percentages(self):
        """

        """
        # insert 2 countries, 1 region, adds up to 100%
        # 2 transactions
        c1 = iati_factory.CountryFactory(code='AF')
        c2 = iati_factory.CountryFactory(code='AL')
        r1 = iati_factory.RegionFactory(code='998')
        currency = iati_factory.CurrencyFactory(code='EUR')

        rc1 = iati_factory.ActivityRecipientCountryFactory(
            activity=self.activity,
            country=c1,
            percentage=30
        )

        rc2 = iati_factory.ActivityRecipientCountryFactory(
            activity=self.activity,
            country=c2,
            percentage=45
        )

        rr1 = iati_factory.ActivityRecipientRegionFactory(
            activity=self.activity,
            region=r1,
            percentage=25
        )

        t1 = TransactionFactory(
            activity=self.activity,
            value=10000,
            value_date='2016-01-01',
            currency=currency
        )

        t2 = TransactionFactory(
            activity=self.activity,
            value=20000,
            value_date='2016-01-01',
            currency=currency
        )


    def test_set_country_region_transaction_without_percentages(self):
        """

        """
        # insert 2 countries, 1 region



    def test_set_sector_transaction_with_percentages(self):
        """

        """
        # insert 3 sectors

    def test_set_sector_transaction_without_percentages(self):
        """

        """
        # insert 3 activity sectors without percentages


        # test if added to transactionsector




class PostSaveFileTestCase(TestCase):
    """
    2.01: post save activity actions called
    """

    def setUp(self):
        self.parser = GenericParser(None)
        version = codelist_models.Version.objects.get(code='2.01')
        self.first_activity = iati_factory.ActivityFactory.create(
            id='IATI-0001',
            iati_identifier='IATI-0001',
            iati_standard_version=version,
            xml_source_ref='source_reference')
        self.second_activity = iati_factory.ActivityFactory.create(
            id='IATI-0002',
            iati_identifier='IATI-0002',
            iati_standard_version=self.first_activity.iati_standard_version,
            xml_source_ref='source_reference')

    @skip('NotImplemented')
    def test_post_save_file(self):
        """
        Check if all required functions are called
        """


    @skip('NotImplemented')
    def test_delete_removed_activities(self):
        """The parser should remove activities that are not in the source any longer

        create 2 activities
        mock a file with 1 of them
        parsing this file should delete the other activity
        """
        root = E('iati-activities', version='2.01')
        xml_activity = E('iati-activity')
        xml_title = E('title', 'Title of activity 1')
        xml_activity.append(xml_title)
        xml_identifier = E('iati-identifier', 'IATI-0001')
        xml_activity.append(xml_identifier)
        root.append(xml_activity)

        self.parser = Parser_201(root)
        # mock non related functions that are called (and that use postgres fts which makes the test fail on sqlite)
        self.parser.update_activity_search_index = MagicMock()

        self.parser.parse_start_datetime = datetime.datetime.now()
        self.parser.iati_source = DatasetFactory(ref='source_reference')
        self.parser.parse_activities(root)

        self.assertEqual(Activity.objects.count(), 1)

