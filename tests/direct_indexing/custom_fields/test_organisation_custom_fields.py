from direct_indexing.custom_fields.organisation_custom_fields import (
    add_all, index_many_to_many_relations, index_total_expenditure
)

TE = 'total-expenditure'


def test_add_all(mocker):
    # Mock index_many_to_many_relations
    mock = mocker.patch('direct_indexing.custom_fields.organisation_custom_fields.index_many_to_many_relations')
    # Test that nothing changes if the data is empty, just converted to a list
    data = {}
    data = add_all(data)
    assert data == [{}]
    mock.assert_called_once()  # called once with the empty dict

    # Test given a list of 2 organisations, the function is called twice
    data = [{}, {}]
    add_all(data)
    assert mock.call_count == len(data) + 1  # +1 because of previous tests


def test_index_many_to_many_relations(mocker):
    # Test that nothing changes if total-expenditure is not present
    data = {}
    index_many_to_many_relations(data)
    assert data == {}

    mock = mocker.patch('direct_indexing.custom_fields.organisation_custom_fields.index_total_expenditure')
    # Test if total-expenditure is present, but not a list, it is converted to a list
    data = {TE: {}}
    index_many_to_many_relations(data)
    assert data == {TE: [{}]}
    mock.assert_called_once()


def test_index_total_expenditure():
    EL = 'expense-line'
    ref = 'ref'
    val = 'value'
    eli = 'total-expenditure.expense-line-index'
    elr = 'total-expenditure.expense-line.ref-index'
    elv = 'total-expenditure.expense-line.val-index'

    # Test that the default fields are created and empty if there is no total-expenditure
    data = {TE: []}
    index_total_expenditure(data, TE)
    assert data[eli] == []
    assert data[elr] == []
    assert data[elv] == []

    # Test that any expense-line is converted to a list
    data = {TE: [{EL: {}}]}
    index_total_expenditure(data, TE)
    assert data[TE][0][EL] == [{}]

    # Test that the expense-line-index is created and populated
    data = {TE: [
        {EL: {val: 10}},
        {EL: {ref: 1, val: 20}},
        {EL: [{ref: 1, val: 30}, {val: 40}, {ref: 2, val: 50}]}
    ]}
    index_total_expenditure(data, TE)
    assert data[eli] == [1, 1, 3]  # one count for each expense-line
    assert data[elr] == [-1, 0, 0, -1, 2]  # -1 for empty,
    assert data[elv] == [0, 0, 0, 1, 2]  # the index of the ref in the list of expense lines, starting at 0
