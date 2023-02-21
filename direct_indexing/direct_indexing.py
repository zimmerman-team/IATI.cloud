import json
import logging

import pysolr
import requests
from django.conf import settings

from direct_indexing.document_summarisation.document_summarisation import document_summarisation
from direct_indexing.metadata.dataset import index_datasets_and_dataset_metadata
from direct_indexing.metadata.publisher import index_publisher_metadata


def run():
    """
    Start the complete indexing process. Should only be used for development purposes.
    Steps:
    . Clear all indices
    . Index the publishers
    . Index the datasets
    """
    logging.info("direct_indexing.run:: Starting a linear indexing process.")
    clear_indices()
    index_publisher_metadata()
    index_datasets_and_dataset_metadata(False, False)


def clear_indices():
    """
    Clear all indices as indicated by the 'cores' variable.
    """
    try:
        cores = ['dataset', 'publisher', 'activity', 'transaction', 'budget', 'result', 'document', 'organisation']
        for core in cores:
            logging.info(f'clear_indices:: Clearing {core} core')
            solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True)
            solr.delete(q='*:*')
            logging.info(f'clear_indices:: Finished clearing {core} core')
        return 'Success'
    except pysolr.SolrError:
        logging.error('clear_indices:: Could not clear indices')
        raise pysolr.SolrError


# Subsets of the indexing process
def run_publisher_metadata():
    result = index_publisher_metadata()
    logging.info(f"run_publisher_metadata:: result: {result}")
    if 'ERROR' in result:
        raise ValueError(result)
    return result


def run_dataset_metadata(update, force_update=False):
    result = index_datasets_and_dataset_metadata(update, force_update)
    logging.info(f"run_dataset_metadata:: result: {result}")
    return result


def run_document_summarisation():
    result = document_summarisation()
    logging.info(f"run_document_summarisation:: result: {result}")
    return result


def drop_removed_data():
    logging.info('drop_removed_data:: Removing all data not found in the latest dataset list')
    dropped_list = []
    existing = []

    # Get the datasets that have been indexed
    url = f'{settings.SOLR_DATASET}/select?fl=name%2Cid%2Ciati_cloud_indexed&indent=true&q.op=OR&q=*%3A*&rows=10000000'
    data = requests.get(url)
    data = data.json()['response']['docs']

    # Get a list of dataset names from the dataset metadata file
    with open(f'{settings.BASE_DIR}/direct_indexing/data_sources/datasets/dataset_metadata.json') as f:
        meta = json.load(f)
        for dataset in meta:
            existing.append(dataset['name'])

    for d in data:
        if d['name'] not in existing:
            dropped_list.append(d['name'])

    # For every core with dataset data, delete the data for the dropped datasets identified with the dataset.name field
    for core in ['activity', 'transaction', 'result', 'budget']:
        solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True)
        for d_name in dropped_list:
            if len(solr.search(f'dataset.name:"{d_name}"')) > 0:
                solr.delete(q=f'dataset.name:"{d_name}"')
    solr = pysolr.Solr(settings.SOLR_DATASET, always_commit=True)
    for d_name in dropped_list:
        if len(solr.search(f'name:"{d_name}"')) > 0:
            solr.delete(q='name:{d_name}')
