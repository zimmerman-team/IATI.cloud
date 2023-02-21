import logging

import requests
from django.conf import settings

from direct_indexing.document_summarisation.const import (
    ALL_FIELDS, DATASET_FIELDS, DOC_LINK_FIELDS, EXTRA_FIELDS, HASH, IDENTIFIER
)


def retrieve_document_links():
    """
    # Retrieve metadata from all activities that have a document link
    # https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/document-link
    # @url is a must have for every document link.
    """
    logging.info('_retrieve_document_links:: Retrieving document links from Solr')
    data_metadata_fields = '%2C'.join(ALL_FIELDS)
    query = 'document-link.url:*'
    doc_url = f'http://localhost:8983/solr/activity/select?fl={data_metadata_fields}&q.op=OR&q={query}&rows=10000000'
    data = requests.get(doc_url).json()['response']['docs']
    return _format_document_links(data)


def _format_document_links(data):
    document_list = []
    # loop over the activities
    for activity in data:
        for index in range(len(activity['document-link.url'])):
            document_list.append(_extract_doc(activity, index))
    return document_list


def _extract_doc(activity, index):
    doc = {}
    for field in EXTRA_FIELDS:
        if field in activity:
            doc[field] = activity[field]
    for field in DOC_LINK_FIELDS:
        if field in activity:
            doc[field] = activity[field][index]
    for field in DATASET_FIELDS:
        if field in activity:
            doc[field] = activity[field]
    return doc


def list_existing_documents():
    """
    Get a unique list of the identifier and hash of the existing documents in the solr core
    """
    logging.info('_list_existing_documents:: Retrieving existing documents from Solr')
    fields = [IDENTIFIER, HASH]
    doc_url = f'{settings.SOLR_DOCUMENT}/select?fl={",".join(fields)}&q.op=OR&q=*:*&rows=10000000'
    existing_data = requests.get(doc_url).json()['response']['docs']
    # Ensure data is available, add NA if not.
    for d in existing_data:
        for field in fields:
            if field not in d:
                d[field] = 'NA'

    ret = []
    ids = []
    for d in existing_data:
        if d[IDENTIFIER] in ids:
            continue
        ret.append(d)
    return ret


def preprocess_documents(data, existing_documents, solr):
    """
    Remove documents from data where the iati-identifier and hash are already in the solr core,
    but the hash has changed. If they match, we skip the document. If they do not exist they are new
    and will be added to the solr core.

    :param data: list of documents
    :param existing_documents: list of existing documents in solr core
    """
    logging.info('_preprocess_documents:: Preprocessing documents')
    # loop over the existing data in form of a list of dicts, and create two lists,
    # one with the iati-identifiers and one with the hashes
    existing_iati_identifiers = []
    existing_hashes = []
    for doc in existing_documents:
        existing_iati_identifiers.append(doc[IDENTIFIER])
        existing_hashes.append(doc[HASH])

    # Filter data and remove documents that are already in the solr core and have been updated
    filtered_data = []
    for doc in data:
        if doc[IDENTIFIER] not in existing_iati_identifiers:
            filtered_data.append(doc)
        else:
            # if the iati-identifier is already in the solr core, check if the hash is the same
            iati_identifier_index = existing_iati_identifiers.index(doc[IDENTIFIER])
            if existing_hashes[iati_identifier_index] != doc[HASH]:
                solr.delete(q=f'{IDENTIFIER}:"{doc[IDENTIFIER]}"')
                filtered_data.append(doc)
    return filtered_data
