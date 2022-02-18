import pysolr
from django.conf import settings

from direct_indexing.metadata.dataset import index_datasets_and_dataset_metadata
from direct_indexing.metadata.publisher import index_publisher_metadata


def clear_indices():
    """
    Clear all indices as indicated by the 'cores' variable.
    """
    cores = ['dataset', 'publisher', 'activity', 'transaction', 'budget', 'result', 'organisation']
    for core in cores:
        solr = pysolr.Solr(f'{settings.SOLR_URL}/{core}', always_commit=True)
        solr.delete(q='*:*')


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
    index_datasets_and_dataset_metadata()
