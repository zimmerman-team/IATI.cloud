from unittest import skip
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.factory import iati_factory
from iati.transaction.factories import TransactionFactory, TransactionTypeFactory
from django.test import TestCase
from iati.transaction.models import TransactionSector, TransactionRecipientCountry, TransactionRecipientRegion
from iati_codelists.factory.codelist_factory import VersionFactory, SectorFactory, SectorVocabularyFactory
from mock import MagicMock
from decimal import Decimal


class PostSaveActivityTestCase(TestCase):
    """
    2.01: post activity actions called
    """

    def setUp(self):
        self.parser = Parser_201(None)

        version = VersionFactory.create(code='2.01')
        self.activity = iati_factory.ActivityFactory.create(
            id='IATI-0001',
            iati_identifier='IATI-0001',
            iati_standard_version=version,
            xml_source_ref='source_reference')

    def setUpTransactionModels(self):
        self.sector_vocabulary = SectorVocabularyFactory()

        self.c1 = iati_factory.CountryFactory(code='AF', name='Afghanistan')
        self.c2 = iati_factory.CountryFactory(code='AL', name='Albania')
        self.r1 = iati_factory.RegionFactory(code='998', name='World-wide, unspecified')
        self.s1 = SectorFactory(code='15160', name='sector A', vocabulary=self.sector_vocabulary)
        self.s2 = SectorFactory(code='15161', name='sector B', vocabulary=self.sector_vocabulary)
        self.currency = iati_factory.CurrencyFactory(code='EUR')

        self.rc1 = iati_factory.ActivityRecipientCountryFactory.create(
            activity=self.activity,
            country=self.c1,
            percentage=None
        )

        self.rc2 = iati_factory.ActivityRecipientCountryFactory.create(
            activity=self.activity,
            country=self.c2,
            percentage=None
        )

        self.rr1 = iati_factory.ActivityRecipientRegionFactory.create(
            activity=self.activity,
            region=self.r1,
            percentage=None
        )

        self.rs1 = iati_factory.ActivitySectorFactory.create(
            activity=self.activity,
            sector=self.s1,
            percentage=None
        )

        self.rs2 = iati_factory.ActivitySectorFactory.create(
            activity=self.activity,
            sector=self.s2,
            percentage=None
        )

        self.tt = TransactionTypeFactory.create(code=1)

        self.t1 = TransactionFactory.create(
            activity=self.activity,
            value=1234,
            value_date='2016-01-01',
            currency=self.currency,
            xdr_value=Decimal(10000),
            transaction_type=self.tt
        )

        self.t2 = TransactionFactory.create(
            activity=self.activity,
            value=2345,
            value_date='2016-01-01',
            currency=self.currency,
            xdr_value=Decimal(20000),
            transaction_type=self.tt
        )

    def test_post_save_models(self):
        """
        Check if correct methods are called
        """
        self.parser.get_model = MagicMock(return_value=self.activity)
        self.parser.set_related_activities = MagicMock()
        self.parser.set_transaction_provider_receiver_activity = MagicMock()
        self.parser.set_derived_activity_dates = MagicMock()
        self.parser.set_activity_aggregations = MagicMock()
        self.parser.update_activity_search_index = MagicMock()
        self.parser.set_country_region_transaction = MagicMock()
        self.parser.set_sector_transaction = MagicMock()

        self.parser.post_save_models()

        self.parser.set_related_activities.assert_called_with(self.activity)
        self.parser.set_transaction_provider_receiver_activity.assert_called_with(self.activity)
        self.parser.set_derived_activity_dates.assert_called_with(self.activity)
        self.parser.set_activity_aggregations.assert_called_with(self.activity)
        self.parser.update_activity_search_index.assert_called_with(self.activity)
        self.parser.set_country_region_transaction.assert_called_with(self.activity)
        self.parser.set_sector_transaction.assert_called_with(self.activity)

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

    def test_set_country_region_transaction_with_percentages(self):
        """
        xdr_value of a transaction should be spliited according to the percentages given on the
        ActivityRecipientCountry / ActivityRecipientRegion
        """
        self.setUpTransactionModels()
        self.rc1.percentage = 30
        self.rc1.save()
        self.rc2.percentage = 45
        self.rc2.save()
        self.rr1.percentage = 25
        self.rr1.save()

        self.parser.set_country_region_transaction(self.activity)

        self.assertEqual(TransactionRecipientCountry.objects.count(), 4)
        self.assertEqual(TransactionRecipientRegion.objects.count(), 2)
        self.assertEqual(TransactionRecipientCountry.objects.filter(
            country=self.c1,
            transaction=self.t1,
            xdr_value=3000
        ).count(), 1)
        self.assertEqual(TransactionRecipientRegion.objects.filter(
            region=self.r1,
            transaction=self.t2,
            xdr_value=5000
        ).count(), 1)

    def test_set_country_region_transaction_without_percentages(self):
        """
        percentages should be split equally among the existing 2 recipient countries and 1 region.
        As a result xdr values should then be split equally.

        """
        self.setUpTransactionModels()
        self.parser.set_country_region_transaction(self.activity)
        self.assertEqual(TransactionRecipientCountry.objects.count(), 4)
        self.assertEqual(TransactionRecipientRegion.objects.count(), 2)

        trc1 = TransactionRecipientCountry.objects.filter(country=self.c1, transaction=self.t1)[0]
        # 10000 / 3
        self.assertEqual(round(trc1.xdr_value), 3333)

        trr1 = TransactionRecipientRegion.objects.filter(region=self.r1,transaction=self.t2)[0]
        # 20000 / 3
        self.assertEqual(round(trr1.xdr_value), 6667)

    def test_set_country_region_transaction_set_on_transaction(self):
        """
        Full transaction.xdr_value should be set on TransactionRecipientCountry/TransactionRecipientRegion
        """
        self.setUpTransactionModels()
        trc = TransactionRecipientCountry(
            country=self.c1,
            transaction=self.t1,
        )
        trc.save()

        trr = TransactionRecipientRegion(
            region=self.r1,
            transaction=self.t2,
        )
        trr.save()

        self.parser.set_country_region_transaction(self.activity)
        self.assertEqual(TransactionRecipientCountry.objects.all()[0].xdr_value, 10000)
        self.assertEqual(TransactionRecipientRegion.objects.all()[0].xdr_value, 20000)

    def test_set_sector_transaction_with_percentages(self):
        """
        xdr_value of a transaction should be spliited according to the percentages given on the ActivitySector
        """
        self.setUpTransactionModels()
        self.rs1.percentage = 25
        self.rs1.save()
        self.rs2.percentage = 75
        self.rs2.save()

        self.parser.set_sector_transaction(self.activity)

        self.assertEqual(TransactionSector.objects.count(), 4)

        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s1,
            transaction=self.t1,
            xdr_value=2500
        ).count(), 1)
        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s2,
            transaction=self.t1,
            xdr_value=7500
        ).count(), 1)

    def test_set_sector_transaction_without_percentages(self):
        """

        """
        self.setUpTransactionModels()
        self.parser.set_sector_transaction(self.activity)
        self.assertEqual(TransactionSector.objects.count(), 4)

        ts1 = TransactionSector.objects.filter(sector=self.s1, transaction=self.t1)[0]
        # 10000 / 2
        self.assertEqual(ts1.xdr_value, 5000)

        ts2 = TransactionSector.objects.filter(sector=self.s2,transaction=self.t2)[0]
        # 20000 / 3
        self.assertEqual(round(ts2.xdr_value), 10000)

    def test_set_sector_transaction_set_on_transaction(self):
        """

        """
        self.setUpTransactionModels()
        sector_vocabulary = SectorVocabularyFactory()

        trc = TransactionSector(
            sector=self.s1,
            transaction=self.t1,
            vocabulary=sector_vocabulary
        )
        trc.save()

        trc2 = TransactionSector(
            sector=self.s2,
            transaction=self.t2,
            vocabulary=sector_vocabulary
        )
        trc2.save()

        self.parser.set_sector_transaction(self.activity)

        trc_updated = TransactionSector.objects.filter(
            sector=self.s1,
            transaction=self.t1
        )
        self.assertEqual(trc_updated.count(), 1)
        self.assertEqual(trc_updated[0].xdr_value, self.t1.xdr_value)
