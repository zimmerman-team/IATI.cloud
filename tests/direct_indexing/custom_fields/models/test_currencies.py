import json

import pytest

from direct_indexing.custom_fields.models.currencies import Currencies

MOCK_PATH = 'direct_indexing.custom_fields.models.currencies.settings.CURRENCIES_JSON'
FILE_NAME = 'currencies.json'


def test_currencies(mocker, tmp_path, fixture_currencies):
    # INTEGRATION
    with open(tmp_path / FILE_NAME, 'w') as file:
        json.dump(fixture_currencies, file)
    # mock settings.CODELISTS_JSON to tmp_path/codelists.json
    mocker.patch(MOCK_PATH, tmp_path / FILE_NAME)
    cu = Currencies()
    assert cu.currencies_list == fixture_currencies


def test_get_currency(mocker, tmp_path, fixture_currencies):
    with open(tmp_path / FILE_NAME, 'w') as file:
        json.dump(fixture_currencies, file)
    # mock settings.CODELISTS_JSON to tmp_path/codelists.json
    mocker.patch(MOCK_PATH, tmp_path / FILE_NAME)
    cu = Currencies()
    # Assert get currencies function returns the correct object, and none if the currency, year or month does not exist
    assert cu.get_currency(3, 2023, 'USD') == fixture_currencies[0]
    assert cu.get_currency(3, 2023, 'EUR') == fixture_currencies[1]
    assert cu.get_currency(3, 2023, 'AUD') is None
    assert cu.get_currency(3, 2050, 'EUR') is None
    assert cu.get_currency(13, 2023, 'EUR') is None
    # Assert None is returned if any of the arguments are None
    assert cu.get_currency(None, 2023, 'USD') is None
    assert cu.get_currency(3, None, 'USD') is None
    assert cu.get_currency(3, 2023, None) is None


def test_convert_currency(mocker, tmp_path, fixture_currencies):
    with open(tmp_path / FILE_NAME, 'w') as file:
        json.dump(fixture_currencies, file)
    # mock settings.CODELISTS_JSON to tmp_path/codelists.json
    mocker.patch(MOCK_PATH, tmp_path / FILE_NAME)
    cu = Currencies()
    # Assert the convert_currency function returns None, None if any of the arguments are None
    assert cu.convert_currency(None, "EUR", 42, 3, 2023) == (None, None)
    assert cu.convert_currency("USD", None, 42, 3, 2023) == (None, None)
    assert cu.convert_currency("USD", "EUR", None, 3, 2023) == (None, None)
    assert cu.convert_currency("USD", "EUR", 42, None, 2023) == (None, None)
    assert cu.convert_currency("USD", "EUR", 42, 3, None) == (None, None)
    # Assert the converted value matches the expected value as per the fixture
    assert cu.convert_currency("USD", "EUR", 42, 3, 2023) == (39.233001205290655, 1.0705273292815591)
    # Assert any type errors resulting in (None, None). Trigger a typeerror by providing a string to the value argument
    assert cu.convert_currency("USD", "EUR", "42", 3, 2023) == (None, None)
    # Assert the return value is the same as the provided value if the source and target are the same
    assert cu.convert_currency("EUR", "EUR", 42, 3, 2023) == (42, 1)
    # Assert the return value is None, None if the source or target are not in the currencies list
    assert cu.convert_currency("AUD", "EUR", 42, 3, 2023) == (None, None)
    assert cu.convert_currency("EUR", "AUD", 42, 3, 2023) == (None, None)
    # Assert the value is returned when XDR is the target
    assert cu.convert_currency("EUR", "XDR", 42, 3, 2023) == (33.6444597384, 0.8010585652)


@pytest.fixture
def fixture_currencies():
    return [
        {
            "year": 2023,
            "month": 3,
            "currency_id": "USD",
            "value": 0.748284087
        },
        {
            "year": 2023,
            "month": 3,
            "currency_id": "EUR",
            "value": 0.8010585652
        },
        {
            "year": 2023,
            "month": 3,
            "currency_id": "XDR",
            "value": 1
        },
    ]
