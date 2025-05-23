from direct_indexing.processing.activity_subtypes import extract_all_subtypes, extract_subtype, process_subtype_dict, _get_budget_year


def test_extract_subtype(mocker):
    transaction = 'transaction'
    # Test an empty list is returned if the subtype in our subtype processing list
    data = {}
    subtype = 'non-existent'
    assert extract_subtype(data, subtype) == []
    # Test an empty list is returned if the subtype is not in the data
    subtype = transaction
    assert extract_subtype(data, subtype) == []

    # Test that if a subtype in the data is a dict, it is converted to a list
    data = {transaction: {}}
    extract_subtype(data, transaction)

    # Test that if a subtype in the data is a list, but the elements are not dicts, we skip
    data = {'title': 'title', transaction: [None, {'value': 1, 'currency': 'USD', 'description': 'test'}]}
    # mock process_subtype_dict
    mock_process = mocker.patch('direct_indexing.processing.activity_subtypes.process_subtype_dict')
    extract_subtype(data, transaction)
    assert mock_process.call_count == len(data.keys())  # once for each key in data


def test_process_subtype_dict(mocker):
    tvu = 'transaction.value-usd'
    bvu = 'budget.value-usd'
    # Test if key is in AVAILABLE_SUBTYPES, it is nothing changes in subtype_dict
    subtype_dict = {'transaction': {'value': 1}}
    expected_res = subtype_dict.copy()
    key = 'transaction'
    mock = mocker.MagicMock()
    res = process_subtype_dict(subtype_dict, key, mock, mock, None, None)
    assert res == expected_res

    # Test if key is in exclude fields we do not include it in the subtype dict
    res = process_subtype_dict(subtype_dict, bvu, mock, mock, [bvu], None)
    assert res == expected_res

    # Test that a specific value which is a dict can be retrieved
    data = {'title': 'title', 'budget': {'value': 1}, tvu: 1.1}
    expected_res = subtype_dict.copy()
    expected_res[tvu] = 1.1
    res = process_subtype_dict(subtype_dict, tvu, mock, data, [], [tvu])
    assert res == expected_res

    # Test that the value of a specific element is extracted from the list
    data = {'title': 'title', 'budget': {'value': 1}, tvu: [1.1]}
    expected_res = subtype_dict.copy()
    expected_res[tvu] = 1.1
    res = process_subtype_dict(subtype_dict, tvu, 0, data, [], [tvu])
    assert res == expected_res

    # Test that additional fields are kept without modification
    expected_res['title'] = 'title'
    res = process_subtype_dict(subtype_dict, 'title', mock, data, [], [])
    assert res == expected_res


def test_extract_all_subtypes(mocker):
    # mock index_many_to_many_relations and extract_subtype
    mock_index = mocker.patch('direct_indexing.processing.activity_subtypes.index_many_to_many_relations')
    mock_extract = mocker.patch('direct_indexing.processing.activity_subtypes.extract_subtype',
                                return_value=[{}])
    data = {}
    subtypes = {}
    subtypes = extract_all_subtypes(subtypes, data)
    mock_index.assert_called_once()
    mock_extract.assert_not_called()
    assert subtypes == {}
    assert data == {}

    data = [
        {
            'budget': {},
            'result': {},
            'transaction': {}
        }, {
            'budget': {},
            'result': {},
            'transaction': {}
        }
    ]
    subtypes = {'budget': [], 'result': [], 'transaction': []}
    extract_all_subtypes(subtypes, data)
    # assert mock_index called 3 times
    assert mock_index.call_count == len(data) + 1  # +1 for the previous test
    assert mock_extract.call_count == len(data) * len(subtypes)  # 2 * 3

def test_get_budget_year():
    # Test with a valid ISO format date
    budget = {'value.value-date': '2023-10-01'}
    assert _get_budget_year(budget) == 2023

    # Test with a valid year in a non-standard format (e.g., "2023-")
    budget = {'value.value-date': '2023-'}
    assert _get_budget_year(budget) == 2023

    # Test with a valid year in a non-standard format (e.g., "-2023")
    budget = {'value.value-date': '-2023'}
    assert _get_budget_year(budget) == 2023

    # Test with a valid year in a slash-separated format (e.g., "2023/10/01")
    budget = {'value.value-date': '2023/10/01'}
    assert _get_budget_year(budget) == 2023

    # Test with an invalid date format
    budget = {'value.value-date': 'invalid-date'}
    assert _get_budget_year(budget) is None

    # Test with an empty date
    budget = {'value.value-date': ''}
    assert _get_budget_year(budget) is None

    # Test with no date key in the budget
    budget = {}
    assert _get_budget_year(budget) is None

    # Test with a valid year embedded in text
    budget = {'value.value-date': 'Budget year: 2023'}
    assert _get_budget_year(budget) == 2023

    # Test with no budget provided
    assert _get_budget_year(None) is None
