# CONFIGURE ENV
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "OIPA.development_settings"

########################### DATASET.PY
import json
import logging
import os
import xml.etree.ElementTree as ET

from django.conf import settings
from pysolr import Solr
from xmljson import badgerfish as bf

from direct_indexing.cleaning.dataset import recursive_attribute_cleaning
from direct_indexing.cleaning.metadata import clean_dataset_metadata
from direct_indexing.custom_fields import custom_fields
from direct_indexing.custom_fields import organisation_custom_fields
from direct_indexing.custom_fields.models import codelists
from direct_indexing.custom_fields.models import currencies as cu
from direct_indexing.metadata.util import index
from direct_indexing.processing import activity_subtypes
from direct_indexing.processing.util import get_dataset_filepath, get_dataset_filetype, get_dataset_version_validity
from direct_indexing.util import index_to_core



DJANGO_SETTINGS_MODULE="OIPA.development_settings"
# Set env DJANGO_SETTINGS_MODULE=OIPA.development_settings




def fun(dataset, update=False):
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
    codelist = codelists.Codelists(download=False)
    dataset = clean_dataset_metadata(dataset)
    dataset_filepath = get_dataset_filepath(dataset)
    print(dataset_filepath)
    valid_version = get_dataset_version_validity(dataset, dataset_filepath)
    print(f'Valid version: {valid_version}')
    dataset_filetype = get_dataset_filetype(dataset)
    dataset_metadata = custom_fields.get_custom_metadata(dataset)
    # Validate the relevant files, mark others as invalid
    validation_status = 'Unvalidated'
    if valid_version:
        # TODO: Enable validation once https://github.com/IATI/validator-services/issues/117 resolved
        # validator_result = get_dataset_validation(dataset['resources'][0]['hash'])
        validator_result = True
        validation_status = 'Valid' if validator_result else 'Invalid'
    print(f'Validation status: {validation_status}')
    # Add the validation status to the dataset
    dataset['dataset_valid'] = validation_status
    indexed = False
    dataset_indexing_result = "Dataset invalid"
    # drop the old data from solr
    # if update:
    #     for url in [settings.SOLR_ACTIVITY, settings.SOLR_BUDGET, settings.SOLR_RESULT, settings.SOLR_TRANSACTION]:
    #         conn = Solr(url)
    #         conn.delete(q='%s:"%s"' % ('dataset.id', dataset['id']), commit=True)

    # Index the relevant datasets,
    # these are activity files of a valid version and that have been successfully validated (not critical)
    if validation_status == 'Valid':
        indexed, dataset_indexing_result = index_dataset(dataset_filepath, dataset_filetype, codelist, currencies,
                                                         dataset_metadata)
    # Add an indexing status to the dataset metadata.
    print(f'Indexing status: {dataset_indexing_result}')
    dataset['iati_cloud_indexed'] = indexed

    # Index the dataset metadata
    logging.info('-- Save the dataset metadata')
    result = index(f'metadata/{dataset["name"]}', dataset, settings.SOLR_DATASET_URL)

    return dataset_indexing_result, result


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
        print("convert_and_save_xml_to_processed_json")
        json_path = convert_and_save_xml_to_processed_json(internal_url, dataset_filetype, codelist, currencies,
                                                           dataset_metadata)
        print("json_path", json_path)
        if json_path:
            result = index_to_core(core_url, json_path, remove=True)
            logging.debug(f'result of indexing {result}')
            if result == 'Successfully indexed':
                return True, result
            return False, result
        return False, "No JSON Path found"
    except Exception as e:  # NOQA
        logging.warning(f'Exception occurred while indexing {dataset_filetype} dataset:\n{internal_url}\n{e}\nTherefore the dataset will not be indexed.')  # NOQA
        return False, str(e)


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
    print("parsed data BADGERFISH")
    # Retrieve activities
    data_found = False
    print(filetype)
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
    print("DEBUG: CLEANING")
    data = recursive_attribute_cleaning(data)
    print("DEBUG: CLEANING DONE")

    print("DEBUG: CUSTOM FIELDS")
    # Add our additional custom fields
    if filetype == 'activity':
        data = custom_fields.add_all(data, codelist, currencies, dataset_metadata)
    if filetype == 'organisation':
        data = organisation_custom_fields.add_all(data)
    print("DEBUG: CUSTOM FIELDS DONE")
    # Activity subtypes
    subtypes = dict()
    if filetype == 'activity':
        for key in activity_subtypes.AVAILABLE_SUBTYPES:
            subtypes[key] = []
        print("EXTRACT SUBTYPES")
        subtypes = activity_subtypes.extract_all_subtypes(subtypes, data)

    print("DEBUG JSON PATH")
    json_path = json_filepath(filepath)
    print("DEBUG JSON DUMP")
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)
    print("DEBUG JSON DUMP DONE")

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
        index_to_core(solr_url, subtype_json_path, remove=True)















################# MAIN RUN
import logging
import requests
from celery import shared_task
from django.conf import settings
from pysolr import Solr
import json 

from direct_indexing.custom_fields.models import codelists
from direct_indexing.processing import dataset as dataset_processing

def retrieve(_, _2):
    path = '/home/zimmerman/Projects/iaticloud/iati.cloud/OIPA/direct_indexing/data_sources/datasets/dataset_metadata.json'
    with open(path) as file:
        return json.load(file)

class DatasetException(Exception):
    def __init__(self, message):
        super().__init__(message)

def direct_indexing_subtask_process_dataset(dataset, update):
    print("start fun")
    dataset_indexing_result, result = fun(dataset, update)
    print("end fun")
    if result == 'Successfully indexed' and dataset_indexing_result == 'Successfully indexed':
        return result
    elif dataset_indexing_result == 'Dataset invalid':
        return dataset_indexing_result
    else:
        raise DatasetException(message=f'Error indexing dataset {dataset["id"]}\nDataset metadata:\n{result}\nDataset indexing:\n{str(dataset_indexing_result)}')  # NOQA


def load_codelists():
    """
    Safe loads codelists.
    """
    logging.info('-- Load currencies and codelists')
    try:
        codelists.Codelists(download=True)
    except requests.exceptions.RequestException:
        logging.error('Codelists not available')
        raise

def prepare_update(_):
    pass

dataset_metadata = retrieve(settings.METADATA_DATASET_URL, 'dataset_metadata')
update = False
# If we are updating instead of refreshing, retrieve dataset ids
if update:
    dataset_metadata, update_bools = prepare_update(dataset_metadata)
else:
    update_bools = [True for _ in dataset_metadata]
load_codelists()
logging.info('-- Walk the metadata')
number_of_datasets = len(dataset_metadata)
for i, dataset in enumerate(dataset_metadata):
    logging.info(f'--- Submitting dataset {i+1} of {number_of_datasets}')
    direct_indexing_subtask_process_dataset(dataset=dataset, update=update_bools[i])

res = '- All Indexing substasks started'
logging.info(res)
# return res
print(res)
