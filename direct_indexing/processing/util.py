import os
import xml.etree.ElementTree as element_tree

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
    if 'organization' in dataset:
        if dataset['organization'] is None:
            return None
        if 'name' in dataset['organization']:
            org_name = dataset['organization']['name']
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

    version = 'extras.iati_version'
    if version in dataset:
        if dataset[version] in VALID_VERSIONS:
            return True
        elif dataset[version] in INVALID_VERSIONS:
            return False
        else:  # Retrieve version from dataset file as the version is not reported in metadata
            return valid_version_from_file(dataset_filepath)

    else:
        return valid_version_from_file(dataset_filepath)


def get_dataset_filetype(dataset):
    """
    Check if the filetype is available in the dataset.

    :param dataset: The dataset to check.
    :return: Nonoe or the filetype, activity or organisation.
    """
    if 'extras.filetype' not in dataset:
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
        if 'version' in root.attrib:
            version = root.attrib['version']
            res = version in VALID_VERSIONS
        return res
    except element_tree.ParseError:
        # If we cannot find a version in the dataset it can not be indexed.
        return False
