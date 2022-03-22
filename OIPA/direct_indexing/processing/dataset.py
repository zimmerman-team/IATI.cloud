import json
import logging
import os
import xml.etree.ElementTree as ET

from django.conf import settings
from xmljson import badgerfish as bf

from direct_indexing.cleaning.dataset import recursive_attribute_cleaning
from direct_indexing.cleaning.metadata import clean_dataset_metadata
from direct_indexing.custom_fields import custom_fields
from direct_indexing.custom_fields.models import codelists
from direct_indexing.custom_fields.models import currencies as cu
from direct_indexing.metadata.util import index
from direct_indexing.processing import activity_subtypes
from direct_indexing.processing.util import get_dataset_filepath, get_dataset_filetype, get_dataset_version_validity
from direct_indexing.util import index_to_core


def fun(dataset):
    """
    Running the dataset means to take the steps.
    . Clean the dataset metadata.
    . Retrieve the filepath of the dataset
    . Check the version validity of the dataset
    . check the filetype of the dataset.
    . Validate the dataset using the IATI Validator
    . Index the dataset to the appropriate solr core.

    :param dataset: The dataset to be indexed.
    :param codelist: An initialized codelist object
    :param currencies: An initialized currencies object
    :return: The updated dataset metadata.
    """
    logging.info(f'Indexing dataset {dataset}')

    currencies = cu.Currencies()
    codelist = codelists.Codelists()
    dataset = clean_dataset_metadata(dataset)
    dataset_filepath = get_dataset_filepath(dataset)
    valid_version = get_dataset_version_validity(dataset, dataset_filepath)
    dataset_filetype = get_dataset_filetype(dataset)
    dataset_metadata = custom_fields.get_custom_metadata(dataset)
    # Validate the relevant files, mark others as invalid
    validation_status = 'Unvalidated'
    if valid_version:
        # TODO: Enable validation once https://github.com/IATI/validator-services/issues/117 resolved
        # validator_result = get_dataset_validation(dataset['resources'][0]['hash'])
        validator_result = True
        validation_status = 'Valid' if validator_result else 'Invalid'

    # Add the validation status to the dataset
    dataset['dataset_valid'] = validation_status
    indexed = False
    # Index the relevant datasets,
    # these are activity files of a valid version and that have been successfully validated (not critical)
    if validation_status == 'Valid':
        indexed = index_dataset(dataset_filepath, dataset_filetype, codelist, currencies, dataset_metadata)
    # Add an indexing status to the dataset metadata.
    dataset['iati_cloud_indexed'] = indexed

    # Index the dataset metadata
    logging.info('-- Save the dataset metadata')
    result = index(f'metadata/{dataset["name"]}', dataset, settings.SOLR_DATASET_URL)
    return result


def index_dataset(internal_url, dataset_filetype, codelist, currencies, dataset_metadata):
    """
    Index the dataset to the correct core.

    :param internal_url: The internal url of the dataset.
    :param dataset_filetype: The filetype of the dataset.
    :param codelist: An initialized codelist object
    :param currencies: An initialized currencies object
    :return: true if indexing successful, false if failed.
    """
    try:
        core_url = settings.SOLR_ACTIVITY_URL if dataset_filetype == 'activity' else settings.SOLR_ORGANISATION_URL
        json_path = convert_and_save_xml_to_processed_json(internal_url, dataset_filetype, codelist, currencies,
                                                           dataset_metadata)
        if json_path:
            result = index_to_core(core_url, json_path)
            logging.debug(f'result of indexing {result}')
            if result == 'Successfully indexed':
                return True
            return False
        return False
    except Exception as e:  # NOQA
        logging.warning(f'Exception occurred while indexing {dataset_filetype} dataset:\n{internal_url}\n{e}\nTherefore the dataset will not be indexed.')  # NOQA
        return False


def convert_and_save_xml_to_processed_json(filepath, filetype, codelist, currencies, dataset_metadata):
    """
    Read the XML into a convertible format and save it to a json file,
    after extracting the activity or organisations from it and cleaning the dataset.

    :param filepath: The filepath of the dataset.
    :param filetype: The filetype of the dataset.
    :param codelist: An initialized codelist object
    :param currencies: An initialized currencies object
    :return: The filepath of the json file.
    """
    parser = ET.XMLParser(encoding='utf-8')
    try:
        etree = ET.parse(filepath, parser=parser)
        tree = ET.tostring(etree.getroot())
    except ET.ParseError:
        return None
    # Convert the tree to json using BadgerFish method.
    data = bf.data(ET.fromstring(tree))
    # Retrieve activities
    data_found = False
    if filetype == 'activity' and 'iati-activities' in data:
        if 'iati-activity' in data['iati-activities']:
            data = data['iati-activities']['iati-activity']
            data_found = True
    elif filetype == 'organisation' and 'iati-organisations' in data:
        if 'iati-organisation' in data['iati-organisations']:
            data = data['iati-organisations']['iati-organisation']
            data_found = True

    if not data_found:
        return data_found
    # Clean the dataset
    data = recursive_attribute_cleaning(data)

    # Add our additional custom fields
    if filetype == 'activity':
        data = custom_fields.add_all(data, codelist, currencies, dataset_metadata)

    # Activity subtypes
    subtypes = dict()
    if filetype == 'activity':
        for key in activity_subtypes.AVAILABLE_SUBTYPES:
            subtypes[key] = []

        subtypes = activity_subtypes.extract_all_subtypes(subtypes, data)

    json_path = json_filepath(filepath)
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)

    if filetype == 'activity':
        index_subtypes(json_path, subtypes)
    return json_path


def json_filepath(filepath):
    """
    os.path provides the splitext function, which splits a
    path into (path, extension) and returns a tuple. Append .json to the path.

    :param filepath: The filepath of the dataset.
    :return: the filepath of the json file.
    """
    converted_path = ''.join((os.path.splitext(filepath)[0], '.json'))
    return converted_path


def index_subtypes(json_path, subtypes):
    """
    Index the subtypes of the activity.
    Subtypes being the transactions, budgets and results stored in the dict.

    First, store them to the appropriate json file. Then index them.

    :param json_path: The filepath of the json file.
    :param subtypes: The dict of subtypes to be stored and indexed.
    :return: None
    """
    for subtype in subtypes:
        subtype_json_path = f'{os.path.splitext(json_path)[0]}_{subtype}.json'
        with open(subtype_json_path, 'w') as json_file:
            json.dump(subtypes[subtype], json_file)

        solr_url = activity_subtypes.AVAILABLE_SUBTYPES[subtype]
        index_to_core(solr_url, subtype_json_path)
