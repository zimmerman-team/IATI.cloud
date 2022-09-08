import logging

import pysolr
from django.conf import settings

from direct_indexing.metadata.dataset import index_datasets_and_dataset_metadata
from direct_indexing.metadata.publisher import index_publisher_metadata


def run():
    """
    Start the complete indexing process.
    Steps:
    . Clear all indices
    . Index the publishers
    . Index the datasets
    """
    clear_indices()
    index_publisher_metadata()
    index_datasets_and_dataset_metadata(False)


def clear_indices():
    """
    Clear all indices as indicated by the 'cores' variable.
    """
    try:
        cores = ['dataset', 'publisher', 'activity', 'transaction', 'budget', 'result', 'organisation']
        for core in cores:
            solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True)
            _solr_out = solr.delete(q='*:*')
            logging.debug(_solr_out)
    except pysolr.SolrError:
        logging.error('Could not clear indices')
        raise pysolr.SolrError


# Subsets of the indexing process
def run_publisher_metadata():
    result = index_publisher_metadata()
    return result


def run_dataset_metadata(update):
    result = index_datasets_and_dataset_metadata(update)
    return result
