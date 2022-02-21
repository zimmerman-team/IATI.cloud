import os
import xml.etree.ElementTree as element_tree

import requests
from django.conf import settings

VALID_VERSIONS = ['2.01', '2.02', '2.03']
INVALID_VERSIONS = ['1.01', '1.02', '1.03', '1.04', '1.05']


def get_dataset_filepath(dataset):
    """
    Dataset files are placed in the following structure:
    ./unzipped location/data/<organisation name>/<dataset name>

    :param dataset: the dataset for which to build a filepath.
    :return: the filepath of the dataset, None if not found.
    """
    org_name = None
    path_string = None
    try:
        if 'organization' in dataset.keys():
            if 'name' in dataset['organization'].keys():
                org_name = dataset['organization']['name']
    except:  # NOQA
        pass
    if org_name:
        dataset_name = dataset['name']  # Name is a required field
        path_string = settings.DATA_EXTRACTED_PATH + '/' + org_name + '/' + dataset_name + '.xml'
    return path_string


def get_dataset_version_validity(dataset, dataset_filepath):
    """
    We consider a dataset valid when it is one of the following
    IATI versions: 2.01, 2.02 or 2.03.

    First, make sure the dataset has a valid path and exists.

    Then, check if the version is reported in the dataset. If so:
        Check if the version is reported and correct.
        Check if the version is reported but incorrect.
        The version can also be reported wrongly (ex.: N/A, NONE)
        If this is the case, do the same as if the version was not reported.
    If not:
        Check if the dataset is valid, because if not, we do not
        need to process any further.

    :param dataset: The dataset to check
    :param dataset_filepath: The path to the dataset
    :return: A boolean indicating the Validation of the dataset
    """
    if not dataset_filepath or not os.path.isfile(dataset_filepath):
        # If we cannot find a file, we cannot index it and it is not valid.
        return False

    if 'extras.iati_version' in dataset.keys():
        if dataset['extras.iati_version'] in VALID_VERSIONS:
            return True
        elif dataset['extras.iati_version'] in INVALID_VERSIONS:
            return False
        else:  # Retrieve version from dataset file as the version is not reported in metadata
            # First check if the dataset is considered valid, otherwise we can skip
            try:
                # Dataset always has a resource which always has a hash
                # TODO: ENABLE DATASET VALIDATION once https://github.com/IATI/validator-services/issues/117 resolved
                # dataset_valid = get_dataset_validation(dataset['resources'][0]['hash'])
                # if not dataset_valid:
                #     return False
                return valid_version_from_file(dataset_filepath)
            except:  # NOQA
                return False
    else:
        return valid_version_from_file(dataset_filepath)


def get_dataset_filetype(dataset):
    """
    Check if the filetype is available in the dataset.

    :param dataset: The dataset to check.
    :return: Nonoe or the filetype, activity or organisation.
    """
    if 'extras.filetype' not in dataset.keys():
        return 'None'
    else:
        return dataset['extras.filetype']


def valid_version_from_file(filepath):
    """
    Extract the value of the iati version from the dataset
    Return True if the dataset is version 2.01, 2.02 or 2.03.
    In any other case return False.

    :param filepath: The path to the dataset file.
    :return: True or False indicating the version being usable.
    """
    parser = element_tree.XMLParser(encoding='utf-8')
    try:
        etree = element_tree.parse(filepath, parser=parser)
        root = etree.getroot()
        res = False
        if 'version' in root.attrib.keys():
            version = root.attrib['version']
            res = version in VALID_VERSIONS
        return res
    except element_tree.ParseError:
        # If we cannot find a version in the dataset it can not be indexed.
        return False


def get_dataset_validation(dataset_hash):
    """
    Retrieve validation status from the public validator.
    https://developer.iatistandard.org/api-details#api=iati-validator-v2&operation=get-pub-get-report
    If for any reason the validator does not work, we should not let this block the process

    :param dataset_hash: The hash of the dataset to be validated
    :return: Boolean indicating if the dataset is valid or not, or True if the validation cannot be retrieved
    """
    validator_url = 'https://api.iatistandard.org/validator/report?hash=' + dataset_hash
    header = {'Ocp-Apim-Subscription-Key': settings.VALIDATOR_API_KEY}
    r = requests.get(validator_url, headers=header)
    res = r.json()

    if 'valid' in res.keys():
        return res['valid']

    return True
