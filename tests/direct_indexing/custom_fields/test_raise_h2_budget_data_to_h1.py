from direct_indexing.custom_fields.raise_h2_budget_data_to_h1 import pull_related_data_to_h1, raise_h2_budget_data_to_h1


def test_raise_h2_budget_data_to_h1(mocker):
    # Test note, data is always a list
    hier = "hierarchy"
    ra = "related-activity"
    rbv = "related_budget_value"

    # mock pull_related_data_to_h1
    mock_pull = mocker.patch('direct_indexing.custom_fields.raise_h2_budget_data_to_h1.pull_related_data_to_h1',
                             return_value=(True, {rbv: [1]}))

    # Test that pull_related_data is not triggered if there is no hierarchy
    data = [{}]
    raise_h2_budget_data_to_h1(data)
    mock_pull.assert_not_called()

    # Test that pull_related_data is not triggered if there is no related-activity
    data = [{hier: 1}]
    raise_h2_budget_data_to_h1(data)
    mock_pull.assert_not_called()

    # Test that pull_related_data is not triggered if hier is not 1
    data = [{hier: 2, ra: {}}]
    raise_h2_budget_data_to_h1(data)
    mock_pull.assert_not_called()

    # Test that ra is converted to a list if it is supplied as a dict
    data = [{hier: 1, ra: {}}]
    raise_h2_budget_data_to_h1(data)
    assert type(data[0][ra]) is list
    # By mocking the return value of pull_related_data_to_h1
    # We can assert that if data present the rbv is added to data's first element
    assert data[0][rbv] == [1]


def test_pull_related_data_to_h1():
    # lists
    related_budget_value = "related_budget_value"
    related_budget_period_start_quarter = "related_budget_period_start_quarter"
    related_budget_period_end_quarter = "related_budget_period_end_quarter"
    related_budget_period_start_iso_date = "related_budget_period_start_iso_date"
    related_budget_period_end_iso_date = "related_budget_period_end_iso_date"

    base_res = {
        related_budget_value: [],
        related_budget_period_start_quarter: [],
        related_budget_period_end_quarter: [],
        related_budget_period_start_iso_date: [],
        related_budget_period_end_iso_date: [],
    }

    hier = "hierarchy"
    ra = "related-activity"
    data = [{hier: 1, ra: {}}]
    expected_res = base_res.copy()

    # Test if there is no related activity, the data is unchanged and railsed values are empty lists
    res_bool, related_data_dict = pull_related_data_to_h1(data, data[0])
    assert related_data_dict == expected_res
    assert not res_bool

    data = [
        {
            "iati-identifier": "act-1",
            "related-activity": [{"ref": "act-2", "type": '2'}, {"ref": "act-3", "type": '2'}]
        },
        {
            "iati-identifier": "act-2",
            "budget": {
                "value": 1,
                "period-start": [
                    {
                        "iso-date": "2019-01-01"
                    }
                ],
                "period-end": [
                    {
                        "iso-date": "2019-04-01"
                    }
                ]
            },
            "related-activity": [{"ref": "act-1", "type": '1'}]
        },
        {
            "iati-identifier": "act-3",
            "budget": {
                "value": 2,
                "period-start": [
                    {
                        "iso-date": "2020-01-01"
                    }
                ],
                "period-end": [
                    {
                        "iso-date": "2020-04-01"
                    }
                ]
            },
            "related-activity": [{"ref": "act-1", "type": '1'}],
            "budget.period-start.quarter": ["1"],
            "budget.period-end.quarter": ["2"]
        }
    ]
    res_bool, related_data_dict = pull_related_data_to_h1(data, data[0])
    assert res_bool
    assert related_data_dict[related_budget_value] == [1, 2]
    assert related_data_dict[related_budget_period_start_quarter] == ["1"]
    assert related_data_dict[related_budget_period_end_quarter] == ["2"]
    assert related_data_dict[related_budget_period_start_iso_date] == ["2019-01-01", "2020-01-01"]
    assert related_data_dict[related_budget_period_end_iso_date] == ["2019-04-01", "2020-04-01"]
