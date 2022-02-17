import logging

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

    logging.info('-- Retrieve codelist and currency information')
    cl = codelists.Codelists()
    cu = currencies.Currencies()

    logging.info('-- Walk the metadata')
    for dataset in dataset_metadata:
        dataset_processing.run(dataset, cl, cu)

    logging.info('-- Save the dataset metadata')
    index('dataset_metadata', dataset_metadata, settings.SOLR_DATASET_URL)

    logging.info('- Indexing complete')
