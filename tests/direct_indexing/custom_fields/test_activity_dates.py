from direct_indexing.custom_fields.activity_dates import FIELDS, activity_dates, extract_activity_dates


def test_fields():
    assert "start-planned" in FIELDS
    assert "start-actual" in FIELDS
    assert "end-planned" in FIELDS
    assert "end-actual" in FIELDS


def test_activity_dates(mocker):
    # mock extract_activity_dates
    mock_extract = mocker.patch('direct_indexing.custom_fields.activity_dates.extract_activity_dates')

    # Test skip if no activity-date
    data = {}
    activity_dates(data)
    mock_extract.assert_not_called()

    # Test conversion to list
    data = {'activity-date': {"type": 1, "iso-date": "test"}}
    activity_dates(data)
    mock_extract.assert_called_once()
    # Check that data['activity-date'] is a list
    assert type(data['activity-date']) is list

    # Test list of dicts calls len() times
    data = {'activity-date': [{"type": 1, "iso-date": "test"}]}
    activity_dates(data)
    assert mock_extract.call_count == len(data['activity-date']) + 1  # +1 for the previous test


def test_extract_activity_dates():
    assert extract_activity_dates({}, {}) == {}
    date = {"type": 1, "iso-date": "test"}
    data = {'activity-date': date}
    ex_res = {'activity-date': date, 'activity-date.start-planned': 'test', 'activity-date.common.start': 'test'}
    assert extract_activity_dates(date, data) == ex_res

    date = {"type": 3, "iso-date": "test"}
    data = {'activity-date': date}
    ex_res = {'activity-date': date, 'activity-date.end-planned': 'test', 'activity-date.common.end': 'test'}
    assert extract_activity_dates(date, data) == ex_res
