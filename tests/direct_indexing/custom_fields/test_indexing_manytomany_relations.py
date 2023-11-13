from direct_indexing.custom_fields.indexing_manytomany_relations import (
    add_field_child_field_children_indexes, add_field_child_field_indexes, add_participating_org_child_indexes,
    add_result_child_indexes, index_many_to_many_relations, iterate_third_level_children
)


def test_index_many_to_many_relations(mocker):
    res = 'result'
    p_org = 'participating-org'
    # mock add_result_child_indexes, add_participating_org_child_indexes
    mock_add_result = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_result_child_indexes')  # NOQA: 501
    mock_add_participating = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_participating_org_child_indexes')  # NOQA: 501

    activity = {}
    # Given an emtpy activity, assert add_result and add p-org are not called
    index_many_to_many_relations(activity)
    mock_add_result.assert_not_called()
    mock_add_participating.assert_not_called()
    assert activity == {}

    # Given an activity with a result which is not a list, assert it is made a list
    activity = {res: {}}
    ex_res = {res: [{}]}
    index_many_to_many_relations(activity)
    assert activity == ex_res

    # Given an activity with a p-org which is not a list, assert it is made a list
    activity = {p_org: {}}
    ex_res = {p_org: [{}]}
    index_many_to_many_relations(activity)
    assert activity == ex_res

    # Given an activity with 2 results and 2 p-orgs, assert add_result and add p-org are called twice
    activity = {res: [{}, {}], p_org: [{}, {}]}
    index_many_to_many_relations(activity)
    assert mock_add_result.call_count == len(activity[res]) + 1  # once per res +1 for the previous test
    assert mock_add_participating.call_count == 2  # once for the list of p-orgs +1 for the previous test


def test_add_participating_org_child_indexes(mocker):
    # mock add_field_child_field_indexes and add_field_child_field_children_indexes
    mock_add_field = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_field_child_field_indexes')  # NOQA: 501
    mock_add_field_children = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_field_child_field_children_indexes')  # NOQA: 501
    add_participating_org_child_indexes(None, None)
    assert mock_add_field.call_count == 6
    mock_add_field_children.assert_called_once()


def test_add_result_child_indexes(mocker):
    t_str = 'test'
    mock_add_field = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_field_child_field_indexes')  # NOQA: 501
    mock_add_field_children = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.add_field_child_field_children_indexes')  # NOQA: 501

    child = t_str
    field = {}
    assert not add_result_child_indexes(field, child)

    field = {t_str: {}}
    add_result_child_indexes(field, child)
    assert field[t_str] == [{}]
    assert mock_add_field.call_count == 2
    mock_add_field_children.assert_called_once()


def test_add_field_child_field_indexes():
    target_field = 'indicator'
    field = 'baseline'
    ibi = 'indicator.baseline-index'

    data = {target_field: [{field: [{}]}]}
    add_field_child_field_indexes(data, target_field, field)
    assert data[ibi] == [0]

    data = {target_field: [{}]}
    add_field_child_field_indexes(data, target_field, field)
    assert data[ibi] == [-1]

    data = {target_field: [{field: {}}]}
    add_field_child_field_indexes(data, target_field, field)
    assert data[ibi] == [0]
    assert data[target_field][0][field] == [{}]

    data = {target_field: [{field: [{}]}, {}, {field: [{}]}]}
    add_field_child_field_indexes(data, target_field, field)
    assert data[ibi] == [0, -1, 1]


def test_add_field_child_field_children_indexes(mocker):
    # mock iterate_third_level_children
    mock_iterate = mocker.patch('direct_indexing.custom_fields.indexing_manytomany_relations.iterate_third_level_children')  # NOQA: 501
    # sample usage: add_field_child_field_children_indexes(field, child, 'period', children=['actual', 'target'])
    target_field = 'indicator'
    field = 'period'
    children = ['actual', 'target']

    data = {
        target_field: [{
            field: {
                'actual': {},
                'target': {}
            }
        }]
    }
    add_field_child_field_children_indexes(data, target_field, field, children)
    # Expect 2 calls, as we have two children.
    assert mock_iterate.call_count == 2


def test_iterate_third_level_children():
    index = 'indicator.period.actual-index'
    target_field = 'indicator'
    field = 'period'
    child = 'actual'
    total_field = 0
    # sample usage: iterate_third_level_children(child, data, field, target, target_field, total_field):

    # Test a single dict
    data = {
        target_field: [{
            field: [{
                'actual': {},
                'target': {}
            }]
        }],
        index: []
    }
    target = data[target_field][0]
    iterate_third_level_children(child, data, field, target, target_field, total_field)
    assert data[index] == [0]

    # Test single value fields
    data = {
        target_field: [{
            field: ['1', '2']
        }],
        index: []
    }
    target = data[target_field][0]
    iterate_third_level_children(child, data, field, target, target_field, total_field)
    assert data[index] == [-1, -1]

    # Test multivalued targets
    data = {
        target_field: [{
            field: [
                {
                    'actual': [{'value': '1'}, {'value': '2'}],
                },
                {
                    'actual': {'value': '3'},
                }
            ]
        }],
        index: []
    }
    target = data[target_field][0]
    iterate_third_level_children(child, data, field, target, target_field, total_field)
    assert data[index] == [0, 2]  # The first starts at 0 with a length of 2, the second starts at index 2 (0+2)

    # Test child not in item
    data = {
        target_field: [{
            field: [{}, {}]
        }],
        index: []
    }
    target = data[target_field][0]
    iterate_third_level_children(child, data, field, target, target_field, total_field)
    assert data[index] == [-1, -1]  # The first starts at 0 with a length of 2, the second starts at index 2 (0+2)
