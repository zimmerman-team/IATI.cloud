import pytest

from direct_indexing.custom_fields.dataset_metadata import dataset_metadata, add_meta_to_activity


def test_dataset_metadata(fixture_dataset):
    assert True


def test_add_meta_to_activity(fixture_dataset):
    # given empty activity and empty metadata, assert nothing changes in activity
    activity = {}
    metadata = {}
    activity = add_meta_to_activity(activity, metadata)
    assert activity == {}
    assert True


@pytest.fixture
def fixture_dataset():
    return {
        "id": "id_test",
    }