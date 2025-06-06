import datetime
import json
import logging

import pysolr
import requests
from django.conf import settings

from direct_indexing.metadata.dataset import aida_drop_dataset, aida_index_dataset, index_datasets_and_dataset_metadata
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


def clear_indices(draft=False):
    """
    Clear all indices as indicated by the 'cores' variable.
    """
    try:
        cores = ['dataset', 'publisher', 'activity', 'transaction', 'budget', 'result',
                 'organisation', 'transaction_trimmed', 'transaction_sdgs', 'budget_split_by_sector']
        if draft:
            cores = [f'draft_{core}' for core in cores]
        for core in cores:
            logging.info(f'clear_indices:: Clearing {core} core')
            solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True, timeout=300)
            solr.delete(q='*:*')
            logging.info(f'clear_indices:: Finished clearing {core} core')
        return 'Success'
    except pysolr.SolrError:
        logging.error('clear_indices:: Could not clear indices')
        raise pysolr.SolrError


def clear_indices_for_core(core):
    """
    Clear all indices as indicated by the 'cores' variable.
    """
    try:
        logging.info(f'clear_indices:: Clearing {core} core')
        solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True, timeout=300)
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


def run_dataset_metadata(update, force_update=False, drop=False):
    result = index_datasets_and_dataset_metadata(update, force_update, drop)
    logging.info(f"run_dataset_metadata:: result: {result}")
    return result


def aida_index(dataset, publisher, ds_name, ds_url, draft=False):
    result, code = aida_index_dataset(dataset, publisher, ds_name, ds_url, draft)
    logging.info(f"aida_index:: result: {result}")
    return result, code


def aida_drop(ds_name, draft):
    result, code = aida_drop_dataset(ds_name, draft)
    logging.info(f"aida_drop:: result: {result}")
    return result, code


def drop_removed_data():
    logging.info('drop_removed_data:: Removing all data not found in the latest dataset list')
    dropped_list = []
    existing = []

    # Get the datasets that have been indexed
    url = f'{settings.SOLR_DATASET}/select?fl=name%2Cid%2Ciati_cloud_indexed%2Ciati_cloud_custom%2Ciati_cloud_aida_sourced&indent=true&q.op=OR&q=*%3A*&rows=10000000'  # NOQA: E501
    data = requests.get(url)
    data = data.json()['response']['docs']
    if len(data) == 0:
        logging.info('drop_removed_data:: No data found in the dataset index, skipping drop')
        return

    # Get a list of dataset names from the dataset metadata file
    with open(f'{settings.BASE_DIR}/direct_indexing/data_sources/datasets/dataset_metadata.json') as f:
        meta = json.load(f)
        for dataset in meta:
            existing.append(dataset['id'])

    for d in data:
        if 'iati_cloud_custom' not in d and 'iati_cloud_aida_sourced' not in d and d['id'] not in existing:
            dropped_list.append(d['id'])

    # For every core with dataset data, delete the data for the dropped datasets identified with the dataset.id field
    for core in ['activity', 'transaction', 'result', 'budget',
                 'transaction_trimmed', 'transaction_sdgs', 'budget_split_by_sector']:
        solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True, timeout=300)
        for d_id in dropped_list:
            if len(solr.search(f'dataset.id:"{d_id}"')) > 0:
                solr.delete(q=f'dataset.id:"{d_id}"')
    solr = pysolr.Solr(settings.SOLR_DATASET, always_commit=True, timeout=300)
    for d_id in dropped_list:
        if len(solr.search(f'id:"{d_id}"')) > 0:
            # solr.delete(q=f'id:{d_id}')
            iati_cloud_removed_date = str(datetime.datetime.now().isoformat())
            # remove last three characters from the string and add Z
            iati_cloud_removed_date = iati_cloud_removed_date[:-3] + 'Z'
            update_data = {
                'id': d_id,
                'iati_cloud_removed_date': {'set': iati_cloud_removed_date},
                'iati_cloud_removed_reason': {'set': 'The dataset was not available in the latest dataset download.'},
                'iati_cloud_indexed': {'set': False},
                'iati_cloud_should_be_indexed': {'set': False}
            }
            # Perform the partial update using atomic update syntax
            solr.add([update_data])
