import logging

import requests
from django.conf import settings

from direct_indexing.custom_fields.models import codelists, currencies
from direct_indexing.metadata.util import download_dataset, index, retrieve
from direct_indexing.processing import dataset as dataset_processing


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

    cl, cu = load_currencies_and_codelists()
    logging.info('-- Walk the metadata')
    number_of_datasets = len(dataset_metadata)
    for i, dataset in enumerate(dataset_metadata):
        logging.info(f'--- Processing dataset {i+1} of {number_of_datasets}')
        dataset_processing.run(dataset, cl, cu)

    logging.info('-- Save the dataset metadata')
    index('dataset_metadata', dataset_metadata, settings.SOLR_DATASET_URL)

    logging.info('- Indexing complete')


def load_currencies_and_codelists():
    """
    Safe loads currencies and codelists.

    :return: a codelist and currency object, can be None.
    """
    logging.info('-- Load currencies and codelists')
    try:
        cl = codelists.Codelists()
    except requests.exceptions.RequestException:
        logging.error('Codelists not available')
        raise

    cu = currencies.Currencies()

    return cl, cu
