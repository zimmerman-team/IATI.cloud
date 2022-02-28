import logging
import subprocess

import pysolr
from django.conf import settings


def clear_core(core_url):
    """
    Clear out the old data from a core

    :param core_url: The url of the core to clear
    :return: None
    """
    try:
        core = pysolr.Solr(core_url, always_commit=True)
        _solr_out = core.delete(q='*:*')
        logging.debug(_solr_out)
    except pysolr.SolrError:
        logging.error(f"Unable to clear core {core_url}")
        raise


def index_to_core(url, json_path):
    """
    Call the Solr post tool to index the json file into the Solr core.

    :param url: The url of the core to index into
    :param json_path: The path to the json file to index
    """
    try:
        _solr_out = subprocess.call([settings.SOLR_POST_TOOL, '-url', url, json_path, '-out', 'no'])
        logging.debug(_solr_out)
    except pysolr.SolrError:
        logging.error(f"Unable to index to {url}")
        raise
