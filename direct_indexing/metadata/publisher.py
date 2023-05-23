import datetime
import logging
import re

from django.conf import settings

from direct_indexing.metadata.util import index, retrieve


def index_publisher_metadata():
    """
    Steps:
    . Download publisher metadata
    . Index publisher metadata

    :return: None
    """
    logging.info('index_publisher_metadata:: - Publisher metadata')
    logging.info('index_publisher_metadata:: -- Retrieve Publisher metadata')
    publishers_metadata = retrieve(settings.METADATA_PUBLISHER_URL, 'publisher_metadata')

    # Process the metadata
    publishers_metadata = _preprocess_publisher_metadata(publishers_metadata)

    # Index the metadata.
    logging.info('index_publisher_metadata:: -- Save JSON publisher metadata')
    indexing_status = index('publisher_metadata', publishers_metadata, settings.SOLR_PUBLISHER_URL)

    logging.info(f'index_publisher_metadata:: result: {indexing_status}')
    return indexing_status


def _preprocess_publisher_metadata(publishers_metadata):
    """
    Process the publisher metadata before indexing.
    Remove any malformed dates from the publisher_first_publish_date field.

    :param publishers_metadata: The publisher metadata to process.
    :return: The processed publisher metadata.
    """
    for publisher in publishers_metadata:
        if 'publisher_first_publish_date' in publisher:

            # regex to detect dates in the format dd.mm.yyyy
            if re.match(r'\d{2}\.\d{2}\.\d{4}', publisher['publisher_first_publish_date']):
                # convert the dd.mm.yyyy to yyyy-mm-ddT00:00:00.000000
                publisher['publisher_first_publish_date'] = datetime.datetime.strptime(
                    publisher['publisher_first_publish_date'], '%d.%m.%Y').strftime('%Y-%m-%dT%H:%M:%S.%f')
    return publishers_metadata
