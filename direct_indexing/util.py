import logging
import os
import re
import subprocess
import urllib.request

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
        logging.info(f'clear_core:: solr_out delete: {_solr_out}')
    except pysolr.SolrError:
        logging.error(f"clear_core:: Unable to clear core {core_url}")
        raise


def index_to_core(url, json_path, remove=False):
    """
    Call the Solr post tool to index the json file into the Solr core.

    :param url: The url of the core to index into
    :param json_path: The path to the json file to index
    :param remove: bool to indicate if the created json file should be removed, defaults to False
    """
    try:
        logging.info("--index to core:: check output")
        solr_out = subprocess.check_output([settings.SOLR_POST_TOOL, '-url', url, json_path],
                                           stderr=subprocess.STDOUT).decode('utf-8')
        result = 'Successfully indexed'
        if 'SolrException' in solr_out or 'Failed to index' in solr_out:
            logging.info("--index to core:: solr_out: " + solr_out)
            message_index = re.search(r'\b(msg)\b', solr_out).start()+5  # +5 to get past the 'msg:'
            solr_out = solr_out[message_index:]
            result = solr_out[:re.search(r'\n', solr_out).start()-1]  # stop at newline excluding the ,
            if remove:
                logging.info("--index to core:: issues in solr parse, remove json dump")
                os.remove(json_path)
        else:
            if remove:
                logging.info("--index to core:: no issues, remove json dump")
                os.remove(json_path)  # On success, remove the json file
        return result
    except subprocess.CalledProcessError as e:
        result = f'Failed to index due to:\n {e}'
        logging.error(f'index_to_core:: error: {result}')
        return result
    except Exception as e:
        logging.info("--index to core:: Uncaught other exception!!" + str(e))
        raise


def datadump_success():
    """
    Check if the most recent IATI Data dump by CodeForIATI was a success.
    Returns true or false based on the above.
    """
    logging.info("datadump_success:: Checking if the most recent CodeForIATI Data Dump was a success.")
    svg_url = 'https://github.com/codeforIATI/iati-data-dump/actions/workflows/refresh_data.yml/badge.svg'
    data_dump_data = urllib.request.urlopen(svg_url)
    data = data_dump_data.read()
    data_dump_data.close()
    # data is a bytestring containing the svg, passing is not in the svg if the action failed
    return b"passing" in data
