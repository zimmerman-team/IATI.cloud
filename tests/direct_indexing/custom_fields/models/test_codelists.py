import json

import pytest

from direct_indexing.custom_fields.models.codelists import SOURCES, Codelists

FILE_NAME = 'codelists.json'


def test_codelist(mocker, tmp_path, requests_mock, fixture_codelists):
    # INTEGRATION
    # Test loading the existing codelists
    # write fixture_codelists to tmp_path/codelists.json
    with open(tmp_path / FILE_NAME, 'w') as file:
        json.dump(fixture_codelists, file)
    # mock settings.CODELISTS_JSON to tmp_path/codelists.json
    mocker.patch('direct_indexing.custom_fields.models.codelists.settings.CODELISTS_JSON', tmp_path / FILE_NAME)
    cl = Codelists(download=False)
    # Assert the codelists_dict is the same as fixture_codelists
    assert cl.get_codelists() == fixture_codelists

    # Test downloading the codelists
    # Remove the codelists.json file
    (tmp_path / FILE_NAME).unlink()
    # mock the requests.get function to return fixture_codelists
    for k, v in SOURCES.items():
        res = [] if k not in fixture_codelists else fixture_codelists[k]
        requests_mock.get(v, json={'data': res})
    cl = Codelists(download=True)
    # Assert the codelists_dict is the same as fixture_codelists
    for key in fixture_codelists:
        assert cl.codelists_dict[key] == fixture_codelists[key]
    # assert the file was re-created @ tmp_path/codelists.json
    assert (tmp_path / FILE_NAME).exists()


def test_get_value(mocker, tmp_path, fixture_codelists):
    with open(tmp_path / FILE_NAME, 'w') as file:
        json.dump(fixture_codelists, file)
    # mock settings.CODELISTS_JSON to tmp_path/codelists.json
    mocker.patch('direct_indexing.custom_fields.models.codelists.settings.CODELISTS_JSON', tmp_path / FILE_NAME)
    cl = Codelists(download=False)

    # Test getting a non-existant codelist results in an empty list
    assert cl.get_value('test', 'test') == []
    # Test getting an existing codelist value
    assert cl.get_value('BudgetStatus', '1') == 'Indicative'
    # Test getting an existing codelist value list
    assert cl.get_value('BudgetStatus', ['1', '2']) == ['Indicative', "Committed"]


@pytest.fixture
def fixture_codelists():
    return {
        "BudgetStatus": [
            {
                "code": "1",
                "name": "Indicative",
                "description": "A non-binding estimate for the described budget.",
                "status": "active"
            },
            {
                "code": "2",
                "name": "Committed",
                "description": "A binding agreement for the described budget.",
                "status": "active"
            }
        ],
        "BudgetType": [
            {
                "code": "1",
                "name": "Original",
                "description": "The original budget allocated to the activity",
                "status": "active"
            },
            {
                "code": "2",
                "name": "Revised",
                "description": "The updated budget for an activity",
                "status": "active"
            }
        ],
    }
