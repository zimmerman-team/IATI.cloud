from direct_indexing.cleaning.dataset import (
    extract_key_value_fields, extract_list_values, extract_literal_values, extract_single_values, list_values,
    recursive_attribute_cleaning, XML_LANG_STR
)


def test_recursive_attribute_cleaning(mocker):
    # Test any key with a @ is replaced with the value of the key without the @
    assert recursive_attribute_cleaning({"@id": 1}) == {"id": 1}
    assert recursive_attribute_cleaning({"id": 1, "@test": 2}) == {"id": 1, "test": 2}
    # Test any key with xml:lang is replaced with lang
    assert recursive_attribute_cleaning({XML_LANG_STR: "en"}) == {"lang": "en"}

    # Test extraction of fields that need to be appended to the dataset
    # This is an integration test and we mock the result of extract_key_value_fields
    key = "value"
    value = [{"$": 1}, {"$": 2}]
    data = {key: value}
    mocker.patch("direct_indexing.cleaning.dataset.extract_key_value_fields", return_value={'value': [1, 2]})
    data = recursive_attribute_cleaning(data)
    assert data == {'value': [1, 2]}
    mocker.stopall()  # Reset mocks

    # Test where data is a list of dicts
    mock_recursive = mocker.patch(
        'direct_indexing.cleaning.dataset.recursive_attribute_cleaning',
        side_effect=recursive_attribute_cleaning,
        autospec=True
    )
    # Call the function under test
    recursive_attribute_cleaning([[{"id": 1}, {"id": 2}], {"id": 3}])
    # Assert that mock_recursive was called for each dictionary in the structure
    assert mock_recursive.call_count == 4  # 2 dictionaries in the list + 1 dictionary outside the list
    # Assert mock recursive was called once with the child list, then once for each dict
    mock_recursive.assert_any_call({"id": 3})
    mock_recursive.assert_any_call({"id": 2})
    mock_recursive.assert_any_call({"id": 1})
    mock_recursive.assert_any_call([{"id": 1}, {"id": 2}])


def test_extract_key_value_fields(mocker):
    # mock extract_literal_values, extract_list_values, extract_single_values, recursive_attribute_cleaning
    mock_elv = mocker.patch('direct_indexing.cleaning.dataset.extract_literal_values', )
    mock_elistv = mocker.patch('direct_indexing.cleaning.dataset.extract_list_values')
    mock_esv = mocker.patch('direct_indexing.cleaning.dataset.extract_single_values')
    mock_rac = mocker.patch('direct_indexing.cleaning.dataset.recursive_attribute_cleaning')

    # Test if the key is a single literal value
    key = "iati-identifier"
    value = {"$": "test"}
    data = {key: value}
    extract_key_value_fields(data, {}, key, value)
    mock_elv.assert_called_once()

    # Test for a list of values with key "value"
    key = "value"
    value = [{"$": 1}, {"$": 2}]
    data = {key: value}
    extract_key_value_fields(data, {}, key, value)
    mock_elistv.assert_called_once()

    # Test for a single value with key "value"
    key = "value"
    value = {"$": 1}
    data = {key: value}
    extract_key_value_fields(data, {}, key, value)
    mock_esv.assert_called_once()

    # Test for a value dict that recursive attribute_cleaning is called
    key = "not_value"
    value = {"test": 1}
    data = {key: value}
    extract_key_value_fields(data, {}, key, value)
    mock_rac.assert_called_once()


def test_extract_literal_values(mocker):
    key = "test"
    # Assert if the value is a list of dicts, the data obj is updated with a list for all the values
    value = [{"$": "value1"}, {"$": "value2"}]
    data = {key: value}
    extract_literal_values(value, key, data)
    assert data[key] == ["value1", "value2"]

    # Assert if the value is a single value, the data obj is updated with the value
    value = {"$": "value"}
    data = {key: value}
    extract_literal_values(value, key, data)
    assert data[key] == "value"


def test_extract_list_values(mocker):
    add_fields = {}
    value = [{"$": 1}, {"$": 2}]
    key = "value"
    data = {key: value}
    # mocker patch list_values to do nothing
    mock_lv = mocker.patch('direct_indexing.cleaning.dataset.list_values')
    add_fields = extract_list_values(add_fields, value, key, data)

    # Assert the expected behavior
    assert data[key] == []  # Check if data[key] is initialized as an empty list

    # Check if add_fields is updated correctly
    expected_add_fields = {
        f'{key}.currency': [],
        f'{key}.value_date': [],
        f'{key}.year': [],
        f'{key}.lang': []
    }
    assert add_fields == expected_add_fields
    # Assert mock_lv was called as many times as there are elements in value
    assert mock_lv.call_count == len(value)


def test_list_values():
    # List values assumes the following:
    # It gets an element, which can be a dict
    # We expect the parent to be a value field
    test_key = "value"
    # Assert if the element is an empty list, the data object is not updated and the add_fields remain unchanged
    test_elem = {}
    test_data = {test_key: []}
    test_data, res = list_values(test_elem, test_data, test_key, {})
    assert res == {}
    assert test_data == {test_key: []}

    # Assert if the element contains a $ key, its value is stored in the provided key array
    test_elem = {"$": 1}
    test_data = {test_key: []}
    test_data, res = list_values(test_elem, test_data, test_key, {})
    assert res == {}
    assert test_data == {test_key: [1]}

    # Assert if the element is missing a $ key, an empty string is stored
    test_elem = {"other": 1}
    test_data = {test_key: []}
    test_data, res = list_values(test_elem, test_data, test_key, {})
    assert res == {}
    assert test_data == {test_key: [" "]}

    # Assert if @currency, @value-date or @year is in the keys, the value is appended to add_fields
    test_elem = {"$": 1, "@currency": "USD"}
    test_data = {test_key: []}
    test_data, res = list_values(test_elem, test_data, test_key, {f"{test_key}.currency": []})
    assert res == {"value.currency": ["USD"]}
    assert test_data == {test_key: [1]}

    # Assert if '@{http://www.w3.org/XML/1998/namespace}lang' is in the value keys
    test_elem = {"$": 1, XML_LANG_STR: "en"}
    test_data = {test_key: []}
    test_data, res = list_values(test_elem, test_data, test_key, {f"{test_key}.lang": []})
    assert res == {"value.lang": ["en"]}

    # Assert if the key is not 'value', an empty field is added to key.lang
    test_elem = {"$": 1}
    test_data = {"test": []}
    test_lang = "test.lang"
    test_data, res = list_values(test_elem, test_data, "test", {test_lang: []})
    assert res == {test_lang: [" "]}


def test_extract_single_values():
    # Assert that if the value is an empty list, we skip
    assert extract_single_values({}, [], "key", {}) == {}
    # Assert if the type of the value is in [int, str, float] we update the data object,
    # and return an unchanged add_fields
    base_key = "value"
    data_obj = {base_key: 1}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {}
    assert data_obj == {base_key: 1}

    # Assert if the type of value is boolean, the bool is converted to 1 or 0
    data_obj = {base_key: False}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {}
    assert data_obj == {base_key: 0}

    # Assert if the type of value is a dict, and $ is in the keys, the main key is set to the value of $
    # $ is only provided in a value dict
    data_obj = {base_key: {"$": 42}}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {}
    assert data_obj == {base_key: 42}

    # Assert if the type of value is an Empty dict the key should be set to " "
    data_obj = {base_key: {}}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {}
    assert data_obj == {base_key: " "}

    # Assert if the value is a dict, and @currency, @value-date or @year is in the keys,
    # the value is appended to add_fields
    data_obj = {base_key: {"@currency": "USD"}}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {"value.currency": "USD"}

    # Assert if '@{http://www.w3.org/XML/1998/namespace}lang' is in the value keys
    data_obj = {base_key: {XML_LANG_STR: "en"}}
    res = extract_single_values({}, data_obj[base_key], base_key, data_obj)
    assert res == {"value.lang": "en"}

    # Assert if the key is not 'value', an empty field is added
    data_obj = {"test": {"$": "bar"}}
    res = extract_single_values({}, data_obj["test"], "test", data_obj)
    test_lang = "test.lang"
    assert res == {test_lang: " "}
