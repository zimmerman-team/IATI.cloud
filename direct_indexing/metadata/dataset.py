import json
import logging
import os

import pysolr
import requests
from celery import shared_task
from django.conf import settings

from direct_indexing.custom_fields.models import codelists
from direct_indexing.metadata.util import download_dataset, retrieve
from direct_indexing.processing import dataset as dataset_processing

INDEX_SUCCESS = 'Successfully indexed'


class DatasetException(Exception):
    def __init__(self, message):
        super().__init__(message)


@shared_task
def subtask_process_dataset(dataset, update):
    dataset_indexing_result, result, should_retry = dataset_processing.fun(dataset, update)
    if result == INDEX_SUCCESS and dataset_indexing_result == INDEX_SUCCESS:
        return result
    elif dataset_indexing_result == 'Dataset invalid':
        return dataset_indexing_result
    elif should_retry:
        raise subtask_process_dataset.retry(countdown=60, max_retries=2, exc=DatasetException(message=f'Error indexing dataset {dataset["id"]}\nDataset metadata:\n{result}\nDataset indexing:\n{str(dataset_indexing_result)}'))  # NOQA
    else:
        return "Dataset was not indexed"
        # commented to prevent false positive exceptions. raise DatasetException(message=f'Error indexing dataset {dataset["id"]}\nDataset metadata:\n{result}\nDataset indexing:\n{str(dataset_indexing_result)}')  # NOQA


def aida_index_dataset(dataset, publisher, dataset_name, dataset_url, draft=False):
    """AIDA specific indexing function."""
    try:
        _aida_download(publisher, dataset_name, dataset_url, dataset)
    except DatasetException as e:
        logging.error(f"aida_index_dataset:: Error downloading dataset: {e}")
        return "Error downloading dataset", 500

    load_codelists()
    dataset_indexing_result, result, _ = dataset_processing.fun(dataset, update=True, draft=draft)
    if result == INDEX_SUCCESS and dataset_indexing_result == INDEX_SUCCESS:
        return result, 200
    elif dataset_indexing_result == 'Dataset invalid':
        return dataset_indexing_result, 200
    else:
        return "Dataset was not indexed", 200


def _aida_download(publisher, dataset_name, dataset_url, dataset):
    # Try to create a directory in direct_indexing/data_sources/datasets/iati-data-main/data named `publisher`
    base_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'data_sources/datasets/iati-data-main'
    ))
    logging.info("BASE PATH: %s", base_path)
    publisher_path = os.path.join(base_path, "data", publisher)
    os.makedirs(publisher_path, exist_ok=True)
    # download the file to the publisher path
    file_path = os.path.join(publisher_path, f"{dataset_name}.xml")
    try:
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Dataset downloaded successfully: {file_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download dataset {dataset_name} from {dataset_url}: {e}")
        raise DatasetException(f"Failed to download dataset {dataset_name} from {dataset_url}: {e}")

    # Save metadata json
    metadata_base_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'data_sources/datasets/iati-data-main'
    ))
    logging.info("BASE PATH: %s", metadata_base_path)
    metadata_publisher_path = os.path.join(metadata_base_path, "metadata", publisher)
    os.makedirs(metadata_publisher_path, exist_ok=True)
    metadata_path = os.path.join(metadata_publisher_path, f"{dataset_name}.json")
    # save dataset as json to metadata_path
    try:
        with open(metadata_path, 'w') as json_file:
            json.dump(dataset, json_file)
    except Exception as e:
        logging.error(f"Failed to save metadata for dataset {dataset_name}: type: {type(e)} stack: {e}")
        raise DatasetException(f"Failed to save metadata for dataset {dataset_name}")


def aida_drop_dataset(dataset_name, draft=False):
    """
    Function to remove any data from IATI.cloud related to a publisher's dataset.

    :param publisher: The publisher name
    :param dataset_name: The name of the dataset
    :return: A message indicating the result of the operation, a HTTP status code.
    """
    try:
        solr_ds = settings.SOLR_DRAFT_DATASET if draft else settings.SOLR_DATASET
        solr = pysolr.Solr(solr_ds, always_commit=True, timeout=300)
        find_data = solr.search(f'name:"{dataset_name}"')
        logging.info(f"aida_drop_dataset:: dataset found: {len(find_data)}")
        if len(find_data) > 0:
            if len(find_data) > 1:
                return "Multiple datasets found with this name, please contact support", 500
            solr.delete(q=f'name:"{dataset_name}"')
    except pysolr.SolrError:
        return "Apologies, but the dataset could not be fully deleted, please contact support", 500

    try:
        core_list = ['activity', 'transaction', 'result', 'budget']
        if draft:
            core_list = [f'draft_{core}' for core in core_list]
        for core in core_list:
            solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True, timeout=300)
            find_data = solr.search(f'dataset.name:"{dataset_name}"')
            logging.info(f"aida_drop_dataset:: {core} found: {len(find_data)}")
            if len(find_data) > 0:
                solr.delete(q=f'dataset.name:"{dataset_name}"')
    except pysolr.SolrError:
        return "Apologies, but the dataset could not be fully deleted, please contact support", 500

    return "Dataset deleted successfully", 200


def index_datasets_and_dataset_metadata(update, force_update, fresh=settings.FRESH):
    """
    Steps:
    . Download all the datasets
    . Download dataset metadata
    . Download codelists and make data available.
    . For every dataset:
        Index that dataset
    . Index all dataset metadata

    :param update: If True, only index datasets that have changed. Determined by a change in the hash
    :param force_update: If True, delete and re-index all datasets.
    :param fresh: If True, download the datasets and metadata again.
    :return: None
    """
    logging.info('index_datasets_and_dataset_metadata:: - Dataset metadata and indexing')
    if fresh:
        # This is a double implementation of a fresh check. In the function itself, we use the ENV value
        # In this implementation, we provide the fresh boolean from the retry function call
        logging.info('index_datasets_and_dataset_metadata:: -- Download datasets')
        download_dataset()
    logging.info('index_datasets_and_dataset_metadata:: -- Retrieve metadata')
    dataset_metadata = retrieve(settings.METADATA_DATASET_URL, 'dataset_metadata', force_update, fresh)

    # If we are updating instead of refreshing, retrieve dataset ids
    if update:
        dataset_metadata, update_bools = prepare_update(dataset_metadata)
    load_codelists()
    logging.info('index_datasets_and_dataset_metadata:: -- Walk the metadata')
    number_of_datasets = len(dataset_metadata)
    for i, dataset in enumerate(dataset_metadata):
        if settings.THROTTLE_DATASET and i % 100 != 0:
            continue
        logging.info(f'index_datasets_and_dataset_metadata:: --- Submitting dataset {i+1} of {number_of_datasets}')
        update_flag = update_bools[i] if update else False
        subtask_process_dataset.delay(dataset=dataset, update=update_flag)
    res = '- All Indexing substasks started'
    logging.info(f'index_datasets_and_dataset_metadata:: result: {res}')
    return res


def retry_unindexed_valid_datasets():
    """
    Retry unindexed valid datasets.

    :return: str describing the result of the operation.
    """
    logging.info('retry_unindexed_valid_datasets:: - Retry unindexed valid datasets')
    # Index all datasets, with update but not fresh, to prevent re-downloading.
    # This will make it so only the datasets with a changed hash will be re-indexed.
    # The only way a hash can be changed in this case, is if we changed the hash in the indexing process.
    # This only happens if `indexed` is set to false, and `should_be_indexed` is set to true.
    index_datasets_and_dataset_metadata(update=True, force_update=False, fresh=False)
    return '- All unindexed valid datasets restarted'


def load_codelists():
    """
    Safe loads codelists.
    """
    logging.info('load_codelists:: -- Load currencies and codelists')
    try:
        codelists.Codelists(download=True)
    except requests.exceptions.RequestException:
        logging.error('load_codelists:: Codelists not available')
        raise


def _get_existing_datasets():
    url = settings.SOLR_DATASET + (
        '/select?q=*:*'
        ' AND id:*&rows=100000&wt=json&fl=resources.hash,id,extras.filetype,iati_cloud_aida_sourced'
    )
    data = requests.get(url).json()['response']['docs']
    datasets = {}
    for doc in data:
        _hash = ""
        if 'resources.hash' in doc:
            _hash = doc['resources.hash'][0]
        _filetype = ""
        if 'extras.filetype' in doc:
            _filetype = doc['extras.filetype']
        datasets[doc['id']] = {'hash': _hash, 'filetype': _filetype}
    return datasets


def prepare_update(dataset_metadata):
    # create a list of new and updated datasets.
    existing_datasets = _get_existing_datasets()
    new_datasets = [d for d in dataset_metadata if d['id'] not in existing_datasets]
    old_datasets = [d for d in dataset_metadata if d['id'] in existing_datasets]
    changed_datasets = [
        d for d in old_datasets if
        ('' if 'hash' not in d['resources'][0] else d['resources'][0]['hash']) != existing_datasets[d['id']]['hash']
    ]
    updated_datasets = new_datasets + changed_datasets
    # This filters out datasets that are indexed by AIDA already, and will not need to be re-indexed.
    # Optionally, we could disable this feature to just re-index the dataset when it pops into the regular processing.
    updated_datasets = [
        d for d in updated_datasets
        if not d.get('iati_cloud_aida_sourced', False)
    ]
    updated_datasets_bools = [False for _ in new_datasets] + [True for _ in changed_datasets]
    return updated_datasets, updated_datasets_bools
