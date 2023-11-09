import pytest

from direct_indexing.processing.util import (
    get_dataset_filepath, get_dataset_filetype, get_dataset_version_validity, valid_version_from_file
)

PATCH_FN = 'direct_indexing.processing.util.valid_version_from_file'


def test_get_dataset_filepath(mocker, fixture_dataset_activity, fixture_dataset_organisation):
    # Test getting a filepath for an activity dataset
    # mock DATA_EXTRACTED_PATH to /iati-data-main/data
    mocker.patch('direct_indexing.processing.util.settings.DATA_EXTRACTED_PATH', '/iati-data-main/data')
    assert get_dataset_filepath(fixture_dataset_activity) == "/iati-data-main/data/fcdo/fcdo-set-1.xml"
    assert get_dataset_filepath(fixture_dataset_organisation) == "/iati-data-main/data/fcdo/fcdo-org.xml"

    # Test a dataset with an organisation field but no name
    assert get_dataset_filepath({"organization": {"Test": "Test"}}) is None
    # Test a dataset with an organisation field which is none
    assert get_dataset_filepath({"organization": None}) is None
    # Test a dataset with no organisation field
    assert get_dataset_filepath({}) is None

    # Test the function with None as its argument returns None
    assert get_dataset_filepath(None) is None


def test_get_dataset_version_validity(mocker, tmp_path):
    field_name = 'extras.iati_version'
    file_path = tmp_path / "fcdo-set-1.xml"
    # Test the function returns False if the dataset_filepath is None or the file does not exist at that path
    assert not get_dataset_version_validity({}, None)
    assert not get_dataset_version_validity({}, file_path)
    # Mock the valid_version_from_file function to return True
    mocker.patch(PATCH_FN, return_value=True)

    # Create test file
    with open(file_path, 'w') as file:
        file.write("<xml>test</xml>")

    assert get_dataset_version_validity({field_name: '2.03'}, file_path)
    assert not get_dataset_version_validity({field_name: '1.01'}, file_path)
    assert get_dataset_version_validity({field_name: '0.0'}, file_path)
    assert get_dataset_version_validity({}, file_path)

    # Test that if the function raises an exception, it returns False
    mocker.patch(PATCH_FN, side_effect=Exception)
    assert not get_dataset_version_validity({}, file_path)


def test_get_dataset_filetype(mocker):
    # Test the function returns None if the dataset is None
    assert get_dataset_filetype(None) == "None"
    # Test the function returns None if the dataset has no extras.filetype field
    assert get_dataset_filetype({}) == "None"
    # Test the function returns the correct filetype if the dataset has an extras.filetype field
    assert get_dataset_filetype({'extras.filetype': 'activity'}) == "activity"
    assert get_dataset_filetype({'extras.filetype': 'organisation'}) == "organisation"
    # Test that if the function raises an exception, it returns False
    mocker.patch('direct_indexing.processing.util.get_dataset_filetype', side_effect=Exception)
    assert get_dataset_filetype({}) == "None"


def test_valid_version_from_file(tmp_path):
    file_path = tmp_path / "fcdo-set-1.xml"

    # Test with an XML file not containing the version
    with open(file_path, 'w') as file:
        file.write("<xml>test</xml>")
    assert not valid_version_from_file(file_path)

    # Test with an XML file containing the version
    with open(file_path, 'w') as file:
        file.write("<xml version='2.03'>test</xml>")
    assert valid_version_from_file(file_path)

    # Test with an XML file without a rood node resulting in a ParseError
    with open(file_path, 'w') as file:
        file.write("")
    assert not valid_version_from_file(file_path)


@pytest.fixture
def fixture_dataset_activity():
    return {
        "owner_org": "4da32e41-a060-4d75-86c1-4b627eb22647",
        "maintainer": None,
        "relationships_as_object": [],
        "private": False,
        "maintainer_email": None,
        "num_tags": 0,
        "publisher_country": "GB",
        "id": "e2fcee3e-a445-4093-a74c-34eeed942221",
        "metadata_created": "2023-02-02T09:53:55.415185",
        "metadata_modified": "2023-10-29T05:49:15.331301",
        "author": None,
        "author_email": "iati-feedback@fcdo.gov.uk",
        "state": "active",
        "version": None,
        "license_id": "uk-ogl",
        "type": "dataset",
        "resources": [
            {
                "mimetype": "",
                "cache_url": None,
                "hash": "da84a2a1186334c6edeeef2e608085d3fa43e1f1",
                "description": None,
                "metadata_modified": "2023-10-29T05:49:15.354998",
                "cache_last_updated": None,
                "url": "http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-1.xml",
                "format": "IATI-XML",
                "state": "active",
                "created": "2023-10-29T05:49:12.216564",
                "package_id": "e2fcee3e-a445-4093-a74c-34eeed942221",
                "mimetype_inner": None,
                "last_modified": None,
                "position": 0,
                "size": 7743257,
                "url_type": None,
                "id": "c3bddc8a-8a13-4706-a2eb-15e9b207fe98",
                "resource_type": None,
                "name": None
            }
        ],
        "num_resources": 1,
        "publisher_organization_type": "10",
        "tags": [],
        "title": "FCDO Activity File 1",
        "groups": [],
        "creator_user_id": "ffe50b5a-bfa2-4522-93b6-c2adfc7bee99",
        "publisher_source_type": "primary_source",
        "relationships_as_subject": [],
        "publisher_iati_id": "GB-GOV-1",
        "name": "fcdo-set-1",
        "isopen": True,
        "url": None,
        "notes": "",
        "license_title": "UK Open Government Licence (OGL)",
        "extras": [
            {
                "value": "806",
                "key": "activity_count"
            },
            {
                "value": "",
                "key": "country"
            },
            {
                "value": "2021-06-07 00:00:00",
                "key": "data_updated"
            },
            {
                "value": "activity",
                "key": "filetype"
            },
            {
                "value": "2.03",
                "key": "iati_version"
            },
            {
                "value": "",
                "key": "language"
            },
            {
                "value": "",
                "key": "secondary_publisher"
            },
            {
                "key": "validation_status",
                "value": "Not Found"
            }
        ],
        "license_url": "http://reference.data.gov.uk/id/open-government-licence",
        "organization": {
            "description": "",
            "title": "UK - Foreign, Commonwealth and Development Office",
            "created": "2020-08-19T13:55:48.059928",
            "approval_status": "approved",
            "is_organization": True,
            "state": "active",
            "image_url": "http://iati.fcdo.gov.uk/iati_files/FCDO_logo.png",
            "type": "organization",
            "id": "4da32e41-a060-4d75-86c1-4b627eb22647",
            "name": "fcdo"
        }
    }


@pytest.fixture
def fixture_dataset_organisation():
    return {
        "owner_org": "4da32e41-a060-4d75-86c1-4b627eb22647",
        "maintainer": None,
        "relationships_as_object": [],
        "private": False,
        "maintainer_email": None,
        "num_tags": 0,
        "publisher_country": "GB",
        "id": "3faa890f-b58c-497c-86af-2f6adda0ba1a",
        "metadata_created": "2020-08-21T12:48:04.440044",
        "metadata_modified": "2023-11-03T04:58:51.131135",
        "author": None,
        "author_email": "enquiry@fcdo.gov.uk",
        "state": "active",
        "version": None,
        "license_id": "uk-ogl",
        "type": "dataset",
        "resources": [
            {
                "mimetype": "",
                "cache_url": None,
                "hash": "9241767ac307d58276e11c53f319dfa47b6ea112",
                "description": "",
                "metadata_modified": "2023-11-03T04:58:51.148529",
                "cache_last_updated": None,
                "url": "http://iati.fcdo.gov.uk/iati_files/organisation.xml",
                "format": "IATI-XML",
                "state": "active",
                "created": "2020-09-01T11:35:05.318259",
                "package_id": "3faa890f-b58c-497c-86af-2f6adda0ba1a",
                "mimetype_inner": None,
                "last_modified": None,
                "position": 0,
                "revision_id": "125a6887-14ea-45e7-b12e-4debdc3f64f1",
                "size": 77601,
                "url_type": None,
                "id": "59866027-c13c-4397-8d34-b8890e9b1024",
                "resource_type": None,
                "name": None
            }
        ],
        "num_resources": 1,
        "publisher_organization_type": "10",
        "tags": [],
        "title": "FCDO Organisation File",
        "groups": [],
        "creator_user_id": "ffe50b5a-bfa2-4522-93b6-c2adfc7bee99",
        "publisher_source_type": "primary_source",
        "relationships_as_subject": [],
        "publisher_iati_id": "GB-GOV-1",
        "name": "fcdo-org",
        "isopen": True,
        "url": None,
        "notes": "",
        "license_title": "UK Open Government Licence (OGL)",
        "extras": [
            {
                "value": "",
                "key": "country"
            },
            {
                "value": "2023-11-01 17:10:36",
                "key": "data_updated"
            },
            {
                "value": "organisation",
                "key": "filetype"
            },
            {
                "value": "2.03",
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
                "value": "Success"
            }
        ],
        "license_url": "http://reference.data.gov.uk/id/open-government-licence",
        "organization": {
            "description": "",
            "title": "UK - Foreign, Commonwealth and Development Office",
            "created": "2020-08-19T13:55:48.059928",
            "approval_status": "approved",
            "is_organization": True,
            "state": "active",
            "image_url": "http://iati.fcdo.gov.uk/iati_files/FCDO_logo.png",
            "type": "organization",
            "id": "4da32e41-a060-4d75-86c1-4b627eb22647",
            "name": "fcdo"
        }
    }
