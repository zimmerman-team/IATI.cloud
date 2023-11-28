import pytest

from direct_indexing.custom_fields.dataset_metadata import add_meta_to_activity, dataset_metadata


def test_dataset_metadata(fixture_dataset):
    expected_res = {
        "dataset.id": "id_test",
        "dataset.resources.hash": "cc612755d0b822bb9af82f43e121428634be255a",
        # dataset.resources.test: should not be included
        # dataset.test: should not be included
    }
    metadata = dataset_metadata(fixture_dataset)
    assert metadata == expected_res

    # If resources not in metadata, assert nothing is added
    dataset = {}
    metadata = dataset_metadata(dataset)
    assert metadata == {}


def test_add_meta_to_activity():
    # Given empty activity and empty metadata, assert nothing changes in activity
    activity = {}
    metadata = {}
    activity = add_meta_to_activity(activity, metadata)
    assert activity == {}

    # Given empty activity and metadata, assert metadata is added to activity
    activity = {}
    metadata = {"test": 1}
    activity = add_meta_to_activity(activity, metadata)
    assert activity == {"test": 1}


@pytest.fixture
def fixture_dataset():
    return {
        "id": "id_test",
        "test": 1,
        "resources": [
            {"hash": "cc612755d0b822bb9af82f43e121428634be255a", "test": 1},
        ]
    }
