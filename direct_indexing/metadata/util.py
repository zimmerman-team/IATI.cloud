import json
import logging
import os
import shutil
import urllib
import zipfile

import requests
from django.conf import settings

from direct_indexing.util import index_to_core


def retrieve(url, name=None, force_update=False, fresh=settings.FRESH):
    """
    Retrieve the given url and return the result as a list of dictionaries.

    :param url: The url to retrieve
    :param name: The name of the file on the local disk
    :return: A list of dictionaries
    """
    try:
        logging.info(f'util.retrieve:: Retrieving {url}')
        path = f'{settings.DATASET_PARENT_PATH}/{name}.json'
        if (not fresh) or force_update:
            logging.info('util.retrieve:: Using pre-downloaded dataset')
            with open(path) as file:
                return json.load(file)
        logging.info('util.retrieve:: Downloading data and dumping as json file.')
        metadata_res = requests.get(url).json()
        with open(path, 'w') as file:
            json.dump(metadata_res['result'], file)
        return metadata_res['result']
    except requests.exceptions.RequestException as e:
        logging.error(f'util.retrieve:: Error retrieving {url}, due to {e}')
        raise


def index(name, metadata, url):
    """
    Save the given set of metadata.
    Index the given set of metadata to the given core.

    :param name: The name of the file on the local disk
    :param metadata: The metadata to save
    :param url: The url to the Solr core
    :return: None
    """
    path = f'{settings.DATASET_PARENT_PATH}/{name}.json'
    logging.info(f'util.index:: indexing {path} to {url}')
    with open(path, 'w') as json_file:
        json.dump(metadata, json_file)

    result = index_to_core(url, path)  # Do not remove the metadata file by using default remove=False
    logging.info(f'util.index:: result: {result}')
    return result


def download_dataset():
    """
    Download all of the datasets and store to local disk.

    :return: None
    """
    try:
        if not settings.FRESH:
            logging.info('download_dataset:: -- Using pre-downloaded dataset')
            return  # Assume the dataset is already downloaded and unzipped
        dataset_zip = 'iati-data-main.zip'  # Location of the zip file
        dataset_zip_folder = f'{settings.DATASET_PARENT_PATH}/{os.path.splitext(dataset_zip)[0]}'
        dataset_zip_loc = f'{settings.DATASET_PARENT_PATH}/{dataset_zip}'

        # ---- Download and unzip the IATI Datasets ----
        logging.info('download_dataset:: -- Download the actual Dataset')
        # Download the dataset
        urlopener = urllib.request.URLopener()
        urlopener.retrieve(settings.DATASET_URL, dataset_zip_loc)

        logging.info('download_dataset:: -- Unzip the dataset')
        # Remove any existing previous data
        if os.path.isdir(dataset_zip_folder):
            shutil.rmtree(dataset_zip_folder)
        # Unzip the dataset
        with zipfile.ZipFile(dataset_zip_loc, 'r') as data_zip:
            data_zip.extractall(settings.DATASET_PARENT_PATH)
    except urllib.error.URLError as e:
        logging.error(f'download_dataset:: Error downloading dataset, due to {e}')
        raise
