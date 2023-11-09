# TODO
from direct_indexing.direct_indexing import clear_indices, clear_indices_for_core
import pytest
import pysolr


# Test group: test_run
def test_run_clear_indices_success(mocker):
    # INTEGRATION TEST
    assert True


# Test group: test_clear_indices
def test_clear_indices_clears_all_indices(mocker):
    # UNIT TEST
    solr_instance_mock = mocker.MagicMock()
    mocker.patch('pysolr.Solr', return_value=solr_instance_mock)

    result = clear_indices()
    # Check that the Solr delete method was called
    solr_instance_mock.delete.assert_called_with(q='*:*')
    # Check that `delete` was called 7 times (once for each core)
    assert solr_instance_mock.delete.call_count == 7
    # Check that the output is "success"
    assert result == 'Success'


def test_clear_indices_raises_error(mocker):
    # UNIT TEST
    mocker.patch('pysolr.Solr', side_effect=pysolr.SolrError)
    with pytest.raises(pysolr.SolrError):
        clear_indices()


def test_clear_indices_for_core_clears_all_indices(mocker):
    # UNIT TEST
    solr_instance_mock = mocker.MagicMock()
    mocker.patch('pysolr.Solr', return_value=solr_instance_mock)

    result = clear_indices_for_core("dataset")
    # Check that the Solr delete method was called
    solr_instance_mock.delete.assert_called_with(q='*:*')
    # Check that `delete` was called once
    assert solr_instance_mock.delete.call_count == 1
    # Check that the output is "success"
    assert result == 'Success'


def test_clear_indices_for_core_raises_error(mocker):
    # UNIT TEST
    mocker.patch('pysolr.Solr', side_effect=pysolr.SolrError)
    with pytest.raises(pysolr.SolrError):
        clear_indices_for_core("dataset")


def test_clear_indices_for_core():
    assert True


def test_run_publisher_metadata():
    assert True


def test_run_dataset_metadata():
    assert True


def test_drop_removed_data():
    assert True
