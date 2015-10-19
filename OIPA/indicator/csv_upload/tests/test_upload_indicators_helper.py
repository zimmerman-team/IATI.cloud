import pytest
from geodata.factory import geodata_factory
from geodata.models import Country, City
from indicator.csv_upload import upload_indicators_helper


def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = list(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
            for funcargs in funcarglist])

@pytest.mark.django_db
class TestUploadIndicatorHelper:

    # a map specifying multiple argument sets for a test method
    params = {
        'test_find_country': [
            dict(country_name="Netherlands", iso2="NL", expected="country_nl"),
            dict(country_name="Netherlands", iso2="", expected="country_nl"),
            dict(country_name="No country name", iso2="", expected=None),
        ],
        'test_find_city': [
            dict(country_name="Netherlands", iso2="NL", expected="country_nl"),
            dict(country_name="Netherlands", iso2="", expected="country_nl"),
            dict(country_name="No country name", iso2="", expected=None),
        ],
        'test_get_value': [
            dict(value_csv="1,33", expected="1.33"),
            dict(value_csv=" 1,33 ", expected="1.33"),
            dict(value_csv="NULL", expected=""),
            dict(value_csv="1.33", expected="1.33"),
            dict(value_csv="134134,03133", expected="134134.03133"),
        ]
    }
    
    @skip("To do; rewrite to django tests")
    def test_find_country(self, country_name, iso2, expected):

        country_nl = geodata_factory.CountryFactory.build(
            code='NL',
            name='Netherlands',
            alt_name='Nederland',
        )
        country_nl.save()

        if expected == "country_nl":
            expected = country_nl

        countries = Country.objects.all()

        result = upload_indicators_helper.find_country(country_name, countries, iso2)
        assert expected == result

    @skip("To do; create a test for this function")
    def test_find_city(self, city, expected):
        return None # todo

    @skip("To do; create a test for this function")
    def test_get_value(self, value_csv, expected):
        return None # todo
        # value = upload_indicators_helper.get_value(value_csv)
        # assert expected == value

    @skip("To do; create a test for this function")
    def test_get_countries(self):

        return None # todo

    @skip("To do; create a test for this function")
    def test_get_cities(self):

        return None # todo

    @skip("To do; create a test for this function")
    def test_save_log(self):
        return None # todo

    @skip("To do; create a test for this function")
    def test_save_city_data(self):
        return None # todo

    @skip("To do; create a test for this function")
    def test_save_country_data(self):
        return None # todo

