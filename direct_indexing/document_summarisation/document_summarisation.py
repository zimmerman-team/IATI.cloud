import logging

import pysolr
from django.conf import settings
from summarizer import Summarizer

from direct_indexing.document_summarisation.const import DOC_URL, FORMAT
from direct_indexing.document_summarisation.preprocess import (
    list_existing_documents, preprocess_documents, retrieve_document_links
)
from direct_indexing.document_summarisation.summarise import summarise_document_content, supported_doctype


def document_summarisation():
    """
    Function kickstarts document summarisation.
    Retrieve the document links, preprocess them and index the summaries
    """
    logging.info('document_summarisation:: Starting document summarisation')
    # Set up solr
    solr = pysolr.Solr(settings.SOLR_DOCUMENT, always_commit=True)
    # Create a separate object for each document link in the activity
    data = retrieve_document_links()
    existing_documents = list_existing_documents()
    data = preprocess_documents(data, existing_documents, solr)

    result = index_summaries(data, solr)
    logging.info(f'document_summarisation:: {result}')
    if result == 'Success':
        logging.info('document_summarisation:: Done document summarisation')
        return result
    else:
        logging.error(f'document_summarisation:: Error in document summarisation:\n{result}')
        raise DocumentException(result)


class DocumentException(Exception):
    def __init__(self, message):
        super().__init__(message)


def index_summaries(data, solr):
    try:
        logging.info('index_summaries:: Indexing summaries')
        model = Summarizer()
        for document in data:
            if not supported_doctype(document[FORMAT]):
                continue
            summarised_text = summarise_document_content(document[DOC_URL], document[FORMAT], model)
            if summarised_text == 'Not extractable':
                document['content-extraction-status'] = 'Not extractable'
            else:
                document['content-extraction-status'] = 'Extracted'
            document['summary'] = summarised_text
            solr.add(document)
        logging.info('index_summaries:: Done indexing summaries')
        return "Success"
    except TypeError as e:
        logging.error(f'index_summaries:: Error indexing summaries:\n{e}')
        return f'error: {e}'
