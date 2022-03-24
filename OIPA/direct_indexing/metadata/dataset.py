import logging

import requests
from celery import shared_task
from django.conf import settings

from direct_indexing.custom_fields.models import codelists
from direct_indexing.metadata.util import download_dataset, retrieve
from direct_indexing.processing import dataset as dataset_processing


@shared_task
def direct_indexing_subtask_process_dataset(dataset):
    dataset_indexing_result, result = dataset_processing.fun(dataset)
    if result == 'Successfully indexed' and dataset_indexing_result == 'Successfully indexed':
        return result
    elif dataset_indexing_result == 'Dataset invalid':
        return dataset_indexing_result
    else:
        raise Exception(f'Error indexing dataset {dataset["id"]}\nDataset metadata:\n{result}\nDataset indexing:\n{str(dataset_indexing_result)}')  # NOQA


def index_datasets_and_dataset_metadata():
    """
    Steps:
    . Download all the datasets
    . Download dataset metadata
    . Download codelists and make data available.
    . For every dataset:
        Index that dataset
    . Index all dataset metadata

    :return: None
    """
    logging.info('- Dataset metadata and indexing')
    download_dataset()

    logging.info('-- Retrieve metadata')
    dataset_metadata = retrieve(settings.METADATA_DATASET_URL, 'dataset_metadata')

    load_codelists()
    logging.info('-- Walk the metadata')
    number_of_datasets = len(dataset_metadata)
    for i, dataset in enumerate(dataset_metadata):
        logging.info(f'--- Submitting dataset {i+1} of {number_of_datasets}')
        direct_indexing_subtask_process_dataset.delay(dataset=dataset)
    res = '- All Indexing substasks started'
    logging.info(res)
    return res


def load_codelists():
    """
    Safe loads codelists.
    """
    logging.info('-- Load currencies and codelists')
    try:
        codelists.Codelists(download=True)
    except requests.exceptions.RequestException:
        logging.error('Codelists not available')
        raise
