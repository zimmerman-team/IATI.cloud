from decimal import Decimal
from unittest import skip

from django.test import TestCase

from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.factory import iati_factory
from iati.transaction.factories import TransactionFactory, TransactionTypeFactory
from iati.transaction.models import TransactionSector, TransactionRecipientCountry, TransactionRecipientRegion
from iati_codelists.factory.codelist_factory import VersionFactory, SectorFactory, BudgetTypeFactory, BudgetStatusFactory
from iati_vocabulary.factory.vocabulary_factory import SectorVocabularyFactory
from iati_synchroniser.factory.synchroniser_factory import DatasetFactory
from iati.models import BudgetSector
from iati.parser import post_save


class PostSaveActivityTestCase(TestCase):
    """
    2.01: post activity actions called
    """

    def setUp(self):
        self.parser = Parser_201(None)

        version = VersionFactory.create(code='2.01')
        dataset = DatasetFactory.create(name='dataset-4')
        self.activity = iati_factory.ActivityFactory.create(
            iati_identifier='IATI-0001',
            iati_standard_version=version,
            dataset=dataset)

    def setUpCountriesRegionsSectors(self):
        self.sector_vocabulary_1 = SectorVocabularyFactory()
        self.sector_vocabulary_2 = SectorVocabularyFactory(code="2", name="DAC5")

        self.c1 = iati_factory.CountryFactory(code='AF', name='Afghanistan')
        self.c2 = iati_factory.CountryFactory(code='AL', name='Albania')
        self.r1 = iati_factory.RegionFactory(code='998', name='World-wide, unspecified')
        self.s1 = SectorFactory(code='15160', name='sector A', vocabulary=self.sector_vocabulary_1)
        self.s2 = SectorFactory(code='15161', name='sector B', vocabulary=self.sector_vocabulary_1)
        self.s3 = SectorFactory(code='15162', name='sector C', vocabulary=self.sector_vocabulary_2)
        self.s4 = SectorFactory(code='15163', name='sector D', vocabulary=self.sector_vocabulary_2)
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
            vocabulary=self.sector_vocabulary_1,
            percentage=None
        )

        self.rs2 = iati_factory.ActivitySectorFactory.create(
            activity=self.activity,
            sector=self.s2,
            vocabulary=self.sector_vocabulary_1,
            percentage=None
        )

        self.rs3 = iati_factory.ActivitySectorFactory.create(
            activity=self.activity,
            sector=self.s3,
            vocabulary=self.sector_vocabulary_2,
            percentage=None
        )

        self.rs4 = iati_factory.ActivitySectorFactory.create(
            activity=self.activity,
            sector=self.s4,
            vocabulary=self.sector_vocabulary_2,
            percentage=None
        )

    def setUpBudgetmodels(self):
        self.setUpCountriesRegionsSectors()
        self.bt = BudgetTypeFactory.create(code=1)
        self.bstatus = BudgetStatusFactory.create(code=1)

        self.budget1 = iati_factory.BudgetFactory.create(
            activity=self.activity,
            type=self.bt,
            status=self.bstatus,
            value=1234,
            period_start='2016-01-01',
            period_end='2018-01-01',
            currency=self.currency,
            xdr_value=Decimal(10000)
        )

        self.budget2 = iati_factory.BudgetFactory.create(
            activity=self.activity,
            type=self.bt,
            status=self.bstatus,
            value=2345,
            period_start='2017-01-01',
            period_end='2019-01-01',
            currency=self.currency,
            xdr_value=Decimal(20000)
        )

    def setUpTransactionModels(self):
        self.setUpCountriesRegionsSectors()
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
        percentage of a transaction should be splitted according to the percentages given on the
        ActivityRecipientCountry / ActivityRecipientRegion
        """
        self.setUpTransactionModels()
        self.rc1.percentage = 30
        self.rc1.save()
        self.rc2.percentage = 45
        self.rc2.save()
        self.rr1.percentage = 25
        self.rr1.save()

        post_save.set_country_region_transaction(self.activity)

        self.assertEqual(TransactionRecipientCountry.objects.count(), 4)
        self.assertEqual(TransactionRecipientRegion.objects.count(), 2)
        self.assertEqual(TransactionRecipientCountry.objects.filter(
            country=self.c1,
            transaction=self.t1,
            percentage=30
        ).count(), 1)
        self.assertEqual(TransactionRecipientRegion.objects.filter(
            region=self.r1,
            transaction=self.t2,
            percentage=25
        ).count(), 1)

    def test_set_country_region_transaction_without_percentages(self):
        """
        Percentages should be split equally among the existing 2 recipient countries and 1 region.
        As a result percentages should then be split equally.

        """
        self.setUpTransactionModels()
        post_save.set_country_region_transaction(self.activity)
        self.assertEqual(TransactionRecipientCountry.objects.count(), 4)
        self.assertEqual(TransactionRecipientRegion.objects.count(), 2)

        trc1 = TransactionRecipientCountry.objects.filter(country=self.c1, transaction=self.t1)[0]
        # 10000 / 3
        self.assertEqual(round(trc1.percentage), 33)

        trr1 = TransactionRecipientRegion.objects.filter(region=self.r1, transaction=self.t2)[0]
        # 20000 / 3
        self.assertEqual(round(trr1.percentage), 33)

    def test_set_sector_transaction_with_percentages(self):
        """
        percentage of a transaction should be splitted according to the percentages given on the ActivitySector
        """
        self.setUpTransactionModels()
        self.rs1.percentage = 25
        self.rs1.save()
        self.rs2.percentage = 75
        self.rs2.save()
        self.rs3.percentage = 25
        self.rs3.save()
        self.rs4.percentage = 75
        self.rs4.save()

        post_save.set_sector_transaction(self.activity)

        self.assertEqual(TransactionSector.objects.count(), 8)

        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s1,
            vocabulary=self.sector_vocabulary_1,
            transaction=self.t1,
            percentage=25
        ).count(), 1)
        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s2,
            vocabulary=self.sector_vocabulary_1,
            transaction=self.t1,
            percentage=75
        ).count(), 1)
        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s3,
            transaction=self.t1,
            percentage=25
        ).count(), 1)
        self.assertEqual(TransactionSector.objects.filter(
            sector=self.s4,
            transaction=self.t1,
            percentage=75
        ).count(), 1)

    def test_set_sector_transaction_without_percentages(self):
        """
        percentages should be split equally among the existing 2 sectors.
        As a result percentages should then be split equally.
        """
        self.setUpTransactionModels()
        post_save.set_sector_transaction(self.activity)
        self.assertEqual(TransactionSector.objects.count(), 8)

        ts1 = TransactionSector.objects.filter(sector=self.s1, transaction=self.t1)[0]
        # 10000 / 2
        self.assertEqual(ts1.percentage, 50)

        ts2 = TransactionSector.objects.filter(sector=self.s2, transaction=self.t1)[0]
        # 20000 / 3
        self.assertEqual(round(ts2.percentage), 50)

        ts3 = TransactionSector.objects.filter(sector=self.s3, transaction=self.t1)[0]
        # 10000 / 2
        self.assertEqual(ts1.percentage, 50)

        ts4 = TransactionSector.objects.filter(sector=self.s4, transaction=self.t1)[0]
        # 20000 / 3
        self.assertEqual(round(ts2.percentage), 50)

    def test_set_sector_budget_with_percentages(self):
        """
        percentage of a transaction should be splitted according to the percentages given on the ActivitySector
        """
        self.setUpBudgetmodels()
        self.rs1.percentage = 25
        self.rs1.save()
        self.rs2.percentage = 75
        self.rs2.save()
        self.rs3.percentage = 25
        self.rs3.save()
        self.rs4.percentage = 75
        self.rs4.save()

        post_save.set_sector_budget(self.activity)

        self.assertEqual(BudgetSector.objects.count(), 8)

        self.assertEqual(BudgetSector.objects.filter(
            sector=self.s1,
            budget=self.budget1,
            percentage=25
        ).count(), 1)
        self.assertEqual(BudgetSector.objects.filter(
            sector=self.s2,
            budget=self.budget1,
            percentage=75
        ).count(), 1)
        self.assertEqual(BudgetSector.objects.filter(
            sector=self.s3,
            budget=self.budget1,
            percentage=25
        ).count(), 1)
        self.assertEqual(BudgetSector.objects.filter(
            sector=self.s4,
            budget=self.budget1,
            percentage=75
        ).count(), 1)

    def test_set_sector_budget_without_percentages(self):
        """
        percentages should be split equally among the existing 2 sectors.
        As a result percentages should then be split equally.
        """
        self.setUpBudgetmodels()
        post_save.set_sector_budget(self.activity)
        self.assertEqual(BudgetSector.objects.count(), 8)

        ts1 = BudgetSector.objects.filter(sector=self.s1, budget=self.budget1)[0]
        self.assertEqual(ts1.percentage, 25)

        ts2 = BudgetSector.objects.filter(sector=self.s2, budget=self.budget2)[0]
        self.assertEqual(round(ts2.percentage), 25)

        ts3 = BudgetSector.objects.filter(sector=self.s3, budget=self.budget1)[0]
        self.assertEqual(ts1.percentage, 25)

        ts4 = BudgetSector.objects.filter(sector=self.s4, budget=self.budget2)[0]
        self.assertEqual(round(ts2.percentage), 25)
