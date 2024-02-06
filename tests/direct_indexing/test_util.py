import os
import subprocess
import urllib.request

import pysolr
import pytest

from direct_indexing import util
from iaticloud import settings


# Test clear_core function
def test_clear_core(mocker):
    # Define the core URL
    core_url = "https://example.com/solr/core"

    # Mock the pysolr.Solr instance
    mock_solr = mocker.patch('pysolr.Solr')
    mock_solr_instance = mock_solr.return_value

    # Mock the delete method
    mock_delete = mocker.patch.object(mock_solr_instance, 'delete')

    # Test the clear_core function
    util.clear_core(core_url)

    # Assert that pysolr.Solr was called with the correct core URL and always_commit
    mock_solr.assert_called_with(core_url, always_commit=True)

    # Assert that the delete method was called with '*:*'
    mock_delete.assert_called_with(q='*:*')

    # Assert that clear_core raises its error when encountering a pysolr.SolrError
    mock_delete.side_effect = pysolr.SolrError
    with pytest.raises(pysolr.SolrError):
        util.clear_core(core_url)


# Test index_to_core function
def test_index_to_core(tmp_path, mocker):
    """
    Index to core:
    - Runs solr post tool with the correct arguments URL and JSON path (which file to submit to solr)
        - if the solr post tool fails, returns the error message
        - if the solr post tool succeeds, returns 'Successfully indexed'
    - Removes the JSON file if remove is True
    - If subprocess errors, return that error.
    """
    # SETUP
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    json_path = test_dir / "test_data.json"
    with open(json_path, 'w') as file:
        file.write('{"key": "value"}')

    url = "https://example.com/solr/core"
    OP = "subprocess.check_output"
    # SUCCESSFUL INDEX:
    # Mock subprocess.check_output to simulate success
    mocker.patch(OP, return_value=b"Successfully indexed")
    # Test a successful indexing
    result = util.index_to_core(url, str(json_path), remove=True)
    # Assert that subprocess.check_output was called with the correct arguments
    subprocess.check_output.assert_called_with([
        settings.SOLR_POST_TOOL,
        '-url',
        url,
        str(json_path)
    ], stderr=subprocess.STDOUT)
    # Assert that the function returns 'Successfully indexed' for a successful operation
    assert result == "Successfully indexed"
    # Assert that the file at json_path was not removed, as the remove argument was False
    assert os.path.exists(json_path) is False

    # FAILED INDEX:
    # re-add the file
    with open(json_path, 'w') as file:
        file.write('{"key": "value"}')

    # Mock subprocess.check_output to simulate failure
    mocker.patch(OP, return_value=b"msg: Failed to index\nERROR...")
    # Test a successful indexing
    result = util.index_to_core(url, str(json_path), remove=True)
    # Assert that subprocess.check_output was called with the correct arguments
    subprocess.check_output.assert_called_with([settings.SOLR_POST_TOOL, '-url', url, str(json_path)],
                                               stderr=subprocess.STDOUT)
    # Assert that the function does not return 'Successfully indexed
    assert result != "Successfully indexed"
    # Assert that the file at json_path was removed, as the remove argument was True
    assert os.path.exists(json_path) is False

    # SUBPROCESS ERROR INDEX:
    # Mock subprocess.check_output to simulate failure
    mocker.patch(OP, side_effect=subprocess.CalledProcessError(returncode=1, cmd="solr_post_tool"))
    # Test a failed indexing
    result = util.index_to_core(url, str(json_path), remove=True)
    # Assert that subprocess.check_output was called with the correct arguments
    subprocess.check_output.assert_called_with([settings.SOLR_POST_TOOL, '-url', url, str(json_path)],
                                               stderr=subprocess.STDOUT)
    # Assert that the function returns an error message for a failed operation
    assert "Failed to index due to:" in result

    # Assert that the function raises an exception when other uncaught exceptions are raised
    mocker.patch(OP, side_effect=Exception)
    with pytest.raises(Exception):
        util.index_to_core(url, str(json_path), remove=True)


# Test datadump_success function
def test_datadump_success(mocker):
    # Mock urllib.request.urlopen to return data with "passing" (success)
    mocker.patch('urllib.request.urlopen')
    urllib.request.urlopen.return_value.read.return_value = b'<svg ... passing ...'
    assert util.datadump_success() is True

    # Mock urllib.request.urlopen to return data without "passing" (failure)
    mocker.patch('urllib.request.urlopen')
    urllib.request.urlopen.return_value.read.return_value = b'<svg ... failing ...'
    assert util.datadump_success() is False
