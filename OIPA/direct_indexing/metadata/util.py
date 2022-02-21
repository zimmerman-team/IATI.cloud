import json
import logging
import os
import shutil
import urllib
import zipfile

import requests
from django.conf import settings

from direct_indexing.util import index_to_core


def retrieve(url, name=None):
    """
    Retrieve the given url and return the result as a list of dictionaries.

    :param url: The url to retrieve
    :param name: The name of the file on the local disk
    :return: A list of dictionaries
    """
    try:
        if not settings.FRESH:
            path = f'{settings.HERE_PATH}/{name}.json'
            with open(path) as file:
                return json.load(file)
        metadata_res = requests.get(url).json()
        return metadata_res['result']
    except:  # NOQA
        logging.error(f'Error retrieving {url}')
        raise Exception("A fatal error has occurred.")  # This exception should stop the process


def index(name, metadata, url):
    """
    Save the given set of metadata.
    Index the given set of metadata to the given core.

    :param name: The name of the file on the local disk
    :param metadata: The metadata to save
    :param url: The url to the Solr core
    :return: None
    """
    try:
        path = f'{settings.HERE_PATH}/{name}.json'
        with open(path, 'w') as json_file:
            json.dump(metadata, json_file)

        index_to_core(url, path)
    except:  # NOQA
        logging.error(f'Error indexing {name}')
        raise Exception("A fatal error has occurred.")  # This exception should stop the process


def download_dataset():
    """
    Download all of the datasets and store to local disk.

    :return: None
    """
    try:
        if not settings.FRESH:
            logging.info('-- Using pre-downloaded dataset')
            return  # Assume the dataset is already downloaded and unzipped
        dataset_zip = 'iati-data-main.zip'  # Location of the zip file
        dataset_zip_folder = settings.HERE_PATH + os.path.splitext(dataset_zip)[0]

        # ---- Download and unzip the IATI Datasets ----
        logging.info('-- Download the actual Dataset')
        # Download the dataset
        urlopener = urllib.request.URLopener()
        urlopener.retrieve(settings.DATASET_URL, dataset_zip)

        logging.info('-- Unzip the dataset')
        # Remove any existing previous data
        if os.path.isdir(dataset_zip_folder):
            shutil.rmtree(dataset_zip_folder)
        # Unzip the dataset
        with zipfile.ZipFile(dataset_zip, 'r') as data_zip:
            data_zip.extractall()
    except:  # NOQA
        logging.error('Error downloading dataset')
        raise Exception("A fatal error has occurred.")  # This exception should stop the process
