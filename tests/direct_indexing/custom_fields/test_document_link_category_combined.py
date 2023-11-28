import pytest

from direct_indexing.custom_fields.document_link_category_combined import document_link_category_combined


def test_document_link_category_combined(fixture_data):
    # Test if no document-link-category, assert nothing changes
    dl = 'document-link'
    dlc = 'document-link.category-codes-combined'
    data = {}
    assert document_link_category_combined(data) == {}

    # Test if a document-link is an empty dict, it is converted to a list and ccc is empty
    data = {dl: {}}
    assert document_link_category_combined(data) == {dl: [{}], dlc: []}

    # Test if a category code is a dict, it is converted to a list
    data = {dl: {'category': {}}}
    assert document_link_category_combined(data) == {dl: [{'category': [{}]}], dlc: []}

    # Test if two codes are present, they are both added
    data = fixture_data.copy()
    expected_res = fixture_data.copy()
    expected_res[dlc] = ['1,2']
    assert document_link_category_combined(data) == expected_res


@pytest.fixture
def fixture_data():
    return {'document-link': [{'category': [{'code': '1'}, {'code': '2'}]}]}
