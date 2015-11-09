from django.test import TestCase

from geodata.factory import geodata_factory
from indicator.factory import indicator_factory
from indicator.csv_upload.indicator_parser import IndicatorParser

from indicator.models import Indicator
from indicator.models import IndicatorData
from indicator.models import IndicatorDataValue


class TestUploadIndicatorHelperTestCase(TestCase):

    def setUp(self):
        self.country = geodata_factory.CountryFactory.create(
            code='NL',
            name='Netherlands',
            alt_name='Nederland',
        )

        self.city = geodata_factory.CityFactory.create(
            id=9999,
            name='Amsterdam',
            ascii_name='ascii_amsterdam',
            alt_name='alt_amsterdam',
            namepar='namepar_amsterdam',
            country=self.country
        )

        self.indicator = indicator_factory.IndicatorFactory.create()
        self.parser = IndicatorParser()

    def test_get_city_name_dict(self):

        city_name_dict = self.parser.get_city_name_dict()

        self.assertTrue('nl' in city_name_dict)
        self.assertTrue('amsterdam' in city_name_dict['nl'])
        self.assertEqual(9999, city_name_dict['nl']['amsterdam'])
        self.assertTrue('ascii_amsterdam' in city_name_dict['nl'])
        self.assertEqual(9999, city_name_dict['nl']['ascii_amsterdam'])
        self.assertTrue('alt_amsterdam' in city_name_dict['nl'])
        self.assertEqual(9999, city_name_dict['nl']['alt_amsterdam'])
        self.assertTrue('namepar_amsterdam' in city_name_dict['nl'])
        self.assertEqual(9999, city_name_dict['nl']['namepar_amsterdam'])

    def test_get_country_name_dict(self):

        country_name_dict = self.parser.get_country_name_dict()

        self.assertTrue('nl' in country_name_dict)
        self.assertEqual('NL', country_name_dict['nl'])
        self.assertTrue('netherlands' in country_name_dict)
        self.assertEqual('NL', country_name_dict['netherlands'])
        self.assertTrue('nederland' in country_name_dict)
        self.assertEqual('NL', country_name_dict['nederland'])

    def test_find_country(self):

        country_name_dict = self.parser.get_country_name_dict()

        result_with_iso2 = self.parser.find_country('Netherlands', country_name_dict, 'NL')
        result_without_iso2 = self.parser.find_country('Netherlands', country_name_dict, None)
        result_false_name = self.parser.find_country('Non existent country', country_name_dict, None)
        result_false_iso2 = self.parser.find_country('Netherlands', country_name_dict, 'QQ')

        self.assertEqual(result_with_iso2, self.country)
        self.assertEqual(result_without_iso2, self.country)
        self.assertEqual(result_false_name, None)
        self.assertEqual(result_false_iso2, self.country)

    def test_find_city(self):
        city_name_dict = self.parser.get_city_name_dict()

        result_no_country = self.parser.find_city('Amsterdam', city_name_dict, None)
        result_correct_name = self.parser.find_city('Amsterdam', city_name_dict, self.country)
        result_false_name = self.parser.find_city('Non existent city', city_name_dict, self.country)

        self.assertEqual(result_no_country, None)
        self.assertEqual(result_correct_name, self.city)
        self.assertEqual(result_false_name, None)

    def test_get_value(self):
        correct_value = self.parser.get_value(unicode('1000'))
        incorrect_value = self.parser.get_value(unicode('No numbers'))
        corrected_value = self.parser.get_value(unicode(' 1000,00'))

        self.assertEqual(correct_value, float(1000))
        self.assertEqual(incorrect_value, None)
        self.assertEqual(corrected_value, float(1000))

    def test_save_log(self):
        uploadLogEntry = indicator_factory.CsvUploadLogFactory.build(
            id=1,
            upload=None,
            title=None,
            slug=None,
            link=None,
            description='',
            uploaded_by=None,
            cities_not_found='Berlin, Paris',
            countries_not_found='Germany',
            total_countries_found=10,
            total_countries_not_found=1,
            total_cities_found=5,
            total_cities_not_found=2,
            total_items_saved=15
        )

        log = self.parser.save_log(
            file=None,
            uploaded_by_user=None,
            cities_not_found=['Berlin', 'Paris'],
            countries_not_found=['Germany'],
            total_cities_found=range(5),
            total_countries_found=range(10),
            total_items_saved=15)

        # cant mock the uuid of course
        uploadLogEntry.slug = log.slug

        self.assertEqual(uploadLogEntry, log)

    def test_save_city_data(self):
        saved_data = self.parser.save_city_data(
            city_from_db=self.city,
            selection_type_csv=unicode('selection_type'),
            indicator_from_db=self.indicator,
            year_csv=unicode('2006'),
            value_csv=float(1000)
        )

        indicatorData = IndicatorData.objects.all()

        self.assertEqual(saved_data, True)
        self.assertEqual(1, indicatorData.count())
        self.assertEqual(1, IndicatorDataValue.objects.all().count())
        self.assertEqual(self.city, indicatorData[0].city)
        self.assertEqual(unicode('selection_type'), indicatorData[0].selection_type)

        # same year, different value
        same_year = self.parser.save_city_data(
            city_from_db=self.city,
            selection_type_csv=unicode('selection_type'),
            indicator_from_db=self.indicator,
            year_csv=unicode('2006'),
            value_csv=float(1234)
        )

        indicatorDataValues = IndicatorDataValue.objects.all()

        self.assertEqual(True, same_year)
        self.assertEqual(1, IndicatorData.objects.all().count())
        self.assertEqual(1, indicatorDataValues.count())
        self.assertEqual(1234.00, indicatorDataValues[0].value)


        # different year, different value
        different_year = self.parser.save_city_data(
            city_from_db=self.city,
            selection_type_csv=unicode('selection_type'),
            indicator_from_db=self.indicator,
            year_csv=unicode('2015'),
            value_csv=float(1000)
        )

        self.assertEqual(different_year, True)
        self.assertEqual(1, IndicatorData.objects.all().count())
        self.assertEqual(2, IndicatorDataValue.objects.all().count())


    def test_save_country_data(self):
        saved_data = self.parser.save_country_data(
            country_from_db=self.country,
            city_csv='',
            selection_type_csv=unicode('selection_type'),
            year_csv=unicode('2006'),
            indicator_from_db=self.indicator,
            value_csv=float(1000)
        )

        indicatorData = IndicatorData.objects.all()

        self.assertEqual(saved_data, True)
        self.assertEqual(None, indicatorData[0].city)
        self.assertEqual(self.country, indicatorData[0].country)

        false_data = self.parser.save_country_data(
            country_from_db=self.country,
            city_csv='Has unmatched city',
            selection_type_csv=unicode('selection_type'),
            year_csv=unicode('2006'),
            indicator_from_db=self.indicator,
            value_csv=float(1000)
        )

        self.assertFalse(false_data)

    def test_parse(self):
        import StringIO
        from django.core.files.uploadedfile import InMemoryUploadedFile

        io = StringIO.StringIO()

        text = 'year;year_range;indicator_id;friendly_name;type_data;selection_type;' \
               'deprivation_type;country;city;region;value;description;category\n' \
               '1992;;indicator_id;indicator text;p;Total;;Netherlands;;;13.3;Global_UNHABITAT-DHS;Health\n' \
               '1993;;indicator_id;indicator text;p;Total;;Netherlands;;;13.5;Global_UNHABITAT-DHS;Health\n'

        io.write(text)
        uploaded_file = InMemoryUploadedFile(io, None, 'testindicator.csv', 'csv', io.len, None)
        uploaded_file.seek(0)

        class MockObject(object):
            user = None

        self.parser.parse(uploaded_file, None, MockObject())

        self.assertEqual(2, Indicator.objects.all().count())
        self.assertEqual(1, IndicatorData.objects.all().count())
        self.assertEqual(2, IndicatorDataValue.objects.all().count())

        self.assertEqual('indicator_id', Indicator.objects.all()[1].id)
        self.assertEqual(self.country, IndicatorData.objects.all()[0].country)
        self.assertEqual(13.5, IndicatorDataValue.objects.all()[1].value)
        self.assertEqual(1993, IndicatorDataValue.objects.all()[1].year)

