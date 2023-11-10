from datetime import datetime

import pytest

from direct_indexing.custom_fields.date_quarters import (
    add_date_quarter_fields, recursive_date_fields, retrieve_date_quarter
)


def test_add_date_quarter_fields(fixture_data):
    data = add_date_quarter_fields(fixture_data)
    # Assert transaction.transaction-date.iso-date quarter field is added, the values should be 2,3 based on the fixture
    assert data['transaction.transaction-date.quarter'] == [2, 3]
    # Assert no test.quarter field was made
    assert 'test.quarter' not in data
    # pass


def test_recursive_date_fields(fixture_data):
    original_head = 'transaction'
    original_tail = ['transaction-date']

    # Test if an empty dict is passed, the function returns an empty list
    assert recursive_date_fields({}, '', '') == []

    # Test if a dict is passed, it is converted to a list
    source_data = {original_head: {}}
    data = recursive_date_fields(source_data, original_head, original_tail)
    assert data == []
    assert source_data == {original_head: [{}]}

    # Test if a list is passed, the function is called recursively for each dict in the list
    source_data = fixture_data.copy()
    data = recursive_date_fields(source_data, original_head, original_tail)
    assert data == [2, 3]


def test_retrieve_date_quarter():
    # Test that if the date is not a string nor a datetime object, the function returns None
    res = retrieve_date_quarter(None)
    assert res is None

    # Test that if the value is a string but not a date, the function returns None
    res = retrieve_date_quarter("test")
    assert res is None

    # Test that if the value is a YYYY-MM-DD string, the function returns the correct quarter
    res = retrieve_date_quarter("2019-04-01")
    assert res == 2

    # Test for datetime objects, once for each hardcoded quarter
    for i in range(1, 13):
        res = retrieve_date_quarter(datetime(2019, i, 1))
        if i in [1, 2, 3]:
            assert res == 1
        if i in [4, 5, 6]:
            assert res == 2
        if i in [7, 8, 9]:
            assert res == 3
        if i in [10, 11, 12]:
            assert res == 4


@pytest.fixture
def fixture_data():
    return {
        "transaction": [
            {"transaction-date": [
                {"iso-date": "2018-04-09"}
            ]},
            {"transaction-date": [{
                "iso-date": "2018-09-09"
            }]},
            {"transaction-date": [{
                "test": 1
            }]}
        ],
        "test": 1
    }
