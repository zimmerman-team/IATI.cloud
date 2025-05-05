import json
import urllib
import zipfile

import pytest
import requests

from direct_indexing.metadata.util import download_dataset, index, retrieve

# consts
SETTINGS_FRESH = 'direct_indexing.metadata.util.settings.FRESH'
SETTINGS_DATASET_PARENT_PATH = 'direct_indexing.metadata.util.settings.DATASET_PARENT_PATH'
TEST_URL = 'https://test.com'


def test_retrieve(mocker, tmp_path, sample_data, requests_mock):
    # Create test file
    test_dir = tmp_path / 'test'
    test_dir.mkdir()
    with open(test_dir / 'test.json', 'w') as file:
        json.dump(sample_data, file)
    mocker.patch(SETTINGS_DATASET_PARENT_PATH, test_dir)

    # Test succesfully loading data when force_update = False, settings.FRESH = False
    mocker.patch(SETTINGS_FRESH, False)
    data = retrieve(TEST_URL, 'test', False)
    assert data == sample_data

    # Test succesfully loading data when force_update = True, settings.FRESH = False
    mocker.patch(SETTINGS_FRESH, False)
    data = retrieve(TEST_URL, 'test', True)
    assert data == sample_data

    # Test requests.get with provided url succesfully creates a file @ test_dir/test2.json and returns 'result'
    mocker.patch(SETTINGS_FRESH, True)
    # Mock the json return from requests.get for the test url
    requests_mock.get(TEST_URL, json=sample_data)
    data = retrieve(TEST_URL, 'test2', False)
    assert data == sample_data['result']
    # Assert there is a file called test2.json at test_dir
    assert (test_dir / 'test2.json').exists()

    # Test `retrieve` function raises an requests.exceptions.RequestException
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException)
    mocker.patch(SETTINGS_FRESH, True)
    with pytest.raises(requests.exceptions.RequestException):
        retrieve(TEST_URL, 'test', False)


def test_index(mocker, tmp_path, sample_data):
    # Create test dir
    test_dir = tmp_path / 'test'
    test_dir.mkdir()

    # Mock settings.DATASET_PARENT_PATH to be test_dir
    mocker.patch(SETTINGS_DATASET_PARENT_PATH, test_dir)
    # Mock the index_to_core function to return 'Successfully indexed'
    mocker.patch('direct_indexing.metadata.util.index_to_core', return_value='Successfully indexed')
    index_res = index('test', sample_data, TEST_URL)
    assert index_res == 'Successfully indexed'
    # Assert there is a file called test.json at test_dir
    assert (test_dir / 'test.json').exists()


def test_download_dataset(mocker, tmp_path):
    # Set up test path
    test_dir = tmp_path / 'test'
    test_dir.mkdir()
    idm_dir = test_dir / 'iati-data-main'
    idm_dir.mkdir()
    mocker.patch(SETTINGS_DATASET_PARENT_PATH, test_dir)

    # Test that if not settings.FRESH, we return None and no further behaviour occurs
    mocker.patch("urllib.request.URLopener")
    mocker.patch(SETTINGS_FRESH, False)
    ret_val = download_dataset()
    assert ret_val == None  # NOQA: E711
    assert urllib.request.URLopener.call_count == 0

    # mocks and instances
    mocker.patch(SETTINGS_FRESH, True)
    mocker.patch("urllib.request.URLopener")
    mocker.patch('zipfile.ZipFile')
    download_dataset()

    # Assert idm_dir was removed
    assert not idm_dir.exists()
    # Assert urllib.request.URLopener was called once
    urllib.request.URLopener.assert_called_once()
    # Assert zipfile.ZipFile was called once
    zipfile.ZipFile.assert_called_once()

    # Assert any urllib errors are raised
    mocker.patch('urllib.request.URLopener', side_effect=urllib.error.URLError("Test"))
    with pytest.raises(urllib.error.URLError):
        download_dataset()


@pytest.fixture
def sample_data():
    return {
        'result': [
            {
                'id': '1',
                'name': 'test',
            },
            {
                'id': '2',
                'name': 'test2',
            }
        ]
    }
