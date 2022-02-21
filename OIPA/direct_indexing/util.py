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
        core.delete(q='*:*')
    except: # NOQA
        logging.error(f"Unable to clear core {core_url}")
        raise Exception("A fatal error has occurred.")  # This exception should stop the process


def index_to_core(url, json_path):
    """
    Call the Solr post tool to index the json file into the Solr core.

    :param url: The url of the core to index into
    :param json_path: The path to the json file to index
    """
    try:
        subprocess.call([settings.SOLR_POST_TOOL, '-url', url, json_path, '-out', 'no'])
    except:  # NOQA
        logging.error(f"Unable to index to {url}")
        raise Exception("A fatal error has occurred.")  # This exception should stop the process
