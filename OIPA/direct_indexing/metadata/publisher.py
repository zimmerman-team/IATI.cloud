import logging

from django.conf import settings

from direct_indexing.metadata.util import index, retrieve
from direct_indexing.util import clear_core


def index_publisher_metadata():
    """
    Steps:
    . Download publisher metadata
    . Index publisher metadata

    :return: None
    """
    logging.info('- Publisher metadata')
    logging.info('-- Retrieve Publisher metadata')
    publishers_metadata = retrieve(settings.METADATA_PUBLISHER_URL, 'publisher_metadata')

    # Index the metadata.
    logging.info('-- Save JSON publisher metadata')
    indexing_status = index('publisher_metadata', publishers_metadata, settings.SOLR_PUBLISHER_URL)

    return indexing_status
