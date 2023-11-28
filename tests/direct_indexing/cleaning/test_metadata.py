import pytest

from direct_indexing.cleaning.metadata import clean_dataset_metadata, clean_extras, clean_resources


def test_clean_dataset_metadata(mocker, fixture_dataset_metadata):
    # mock clean_resources and clean_extras
    mock_cr = mocker.patch('direct_indexing.cleaning.metadata.clean_resources')
    mock_ce = mocker.patch('direct_indexing.cleaning.metadata.clean_extras')
    clean_dataset_metadata(fixture_dataset_metadata)
    # Assert mock_cr and mock_ce are called once
    mock_cr.assert_called_once()
    mock_ce.assert_called_once()


def test_clean_resources(fixture_dataset_metadata):
    clean_resources(fixture_dataset_metadata)
    presumed_removed_resources = [
        "mimetype", "cache_url", "description", "cache_last_updated", "mimetype_inner",
        "last_modified", "url_type", "resource_type", "name"
    ]
    presumed_kept_resources = [
        "hash", "metadata_modified", "url", "format", "state", "created", "package_id", "position", "size", "id"
    ]
    # Assert empty values are removed and non-empty values are kept
    for key in presumed_removed_resources:
        assert key not in fixture_dataset_metadata["resources"][0]
    for key in presumed_kept_resources:
        assert key in fixture_dataset_metadata["resources"][0]


def test_clean_extras(fixture_dataset_metadata):
    clean_extras(fixture_dataset_metadata)
    # Check if all the items with empty values are removed from fixture_dataset_metadata["extras"]
    # Assert secondary_publisher not in fixture_dataset_metadata["extras"]
    keys = [item["key"] for item in fixture_dataset_metadata["extras"]]
    assert "secondary_publisher" not in keys
    assert "country" not in keys
    # Check the 6 remaining items are still in the extras
    assert len(keys) == 6
    for key in keys:
        # Assert there is a f'extras.{key}' field in fixture_dataset_metadata
        assert f'extras.{key}' in fixture_dataset_metadata


@pytest.fixture
def fixture_dataset_metadata():
    return {
        # REMOVE
        "owner_org": "5e04afab-3aee-4871-ae8d-c175896c5112",
        "maintainer": None,
        "relationships_as_object": [],
        "private": False,
        "maintainer_email": None,
        "num_tags": 0,
        "id": "9d7eb44f-0b13-422d-9542-0793e785d4fa",
        "metadata_created": "2014-01-15T07:49:08.717792",
        "metadata_modified": "2023-03-10T05:01:33.194172",
        "author": None,
        "author_email": "jasper.hakala@formin.fi",
        "state": "active",
        "version": None,
        "license_id": "other-at",
        "type": "dataset",
        "resources": [
            {
                "mimetype": "",
                "cache_url": "",
                "hash": "asdcd03416fe22532a19d40f625f1e55b2e3fba738f",
                "description": "",
                "metadata_modified": "2022-05-05T23:56:00.301819",
                "cache_last_updated": "",
                "url": "https://formin.finland.fi/opendata/IATI/Finland_total_2012.xml",
                "format": "iati-xml",
                "state": "active",
                "created": "2022-04-20T07:16:11.709336",
                "package_id": "9d7eb44f-0b13-422d-9542-0793e785d4fa",
                "mimetype_inner": "",
                "last_modified": "",
                "position": 0,
                "size": 6845840,
                "url_type": "",
                "id": "47c2ae77-005a-4df9-953d-8a29b0f544ac",
                "resource_type": "",
                "name": ""
            }
        ],
        "num_resources": 1,
        "tags": [],
        "title": "Finland Activity File 2012",
        "groups": [],
        "creator_user_id": "b9a93bc8-247c-4ad9-909f-8531fed1983a",
        "relationships_as_subject": [],
        "name": "finland_mfa-001",
        "isopen": True,
        "url": None,
        "notes": "",
        "license_title": "Other (Attribution)",
        "extras": [
            {
                "value": "2073",
                "key": "activity_count"
            },
            {
                "value": "",
                "key": "country"
            },
            {
                "value": "2019-06-27 12:59:51",
                "key": "data_updated"
            },
            {
                "value": "activity",
                "key": "filetype"
            },
            {
                "value": "2.02",
                "key": "iati_version"
            },
            {
                "value": "en",
                "key": "language"
            },
            {
                "value": "",
                "key": "secondary_publisher"
            },
            {
                "key": "validation_status",
                "value": "Error"
            }
        ],
        "organization": {
            "description": "",
            "title": "Finland - Ministry for Foreign Affairs",
            "created": "2011-11-25T13:21:36.013765",
            "approval_status": "approved",
            "is_organization": True,
            "state": "active",
            "image_url": "",
            "type": "organization",
            "id": "5e04afab-3aee-4871-ae8d-c175896c5112",
            "name": "finland_mfa"
        }
    }
