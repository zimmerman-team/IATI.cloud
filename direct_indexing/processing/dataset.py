import json
import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from django.conf import settings
from pysolr import Solr
from xmljson import badgerfish as bf

from direct_indexing.cleaning.dataset import recursive_attribute_cleaning
from direct_indexing.cleaning.metadata import clean_dataset_metadata
from direct_indexing.custom_fields import custom_fields, organisation_custom_fields
from direct_indexing.custom_fields.models import codelists
from direct_indexing.custom_fields.models import currencies as cu
from direct_indexing.metadata.util import index
from direct_indexing.processing import activity_subtypes
from direct_indexing.processing.util import get_dataset_filepath, get_dataset_filetype, get_dataset_version_validity
from direct_indexing.util import index_to_core


def fun(dataset, update=False, draft=False):
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
    valid_version = get_dataset_version_validity(dataset, dataset_filepath)
    dataset_filetype = get_dataset_filetype(dataset)
    dataset_metadata = custom_fields.get_custom_metadata(dataset)
    # Validate the relevant files, mark others as invalid
    validation_status = 'Valid'
    should_be_indexed = False
    if 'dataset.extras.validation_status' in dataset_metadata:
        validation_status = 'Invalid' if dataset_metadata['dataset.extras.validation_status'] == 'Critical' else 'Valid'

    # Add the validation status to the dataset
    dataset['dataset_valid'] = validation_status
    indexed = False
    dataset_indexing_result = "Dataset invalid"

    _update_drop(update, draft, dataset)

    # Index the relevant datasets,
    # these are activity files of a valid version and that have been successfully validated (not critical)
    if validation_status == 'Valid' and valid_version:
        indexed, dataset_indexing_result, should_be_indexed = index_dataset(dataset_filepath, dataset_filetype,
                                                                            codelist, currencies,
                                                                            dataset_metadata, draft)
    # Add an indexing status to the dataset metadata.
    dataset['iati_cloud_indexed'] = indexed
    dataset['iati_cloud_indexed_datetime'] = str(datetime.now())
    dataset['iati_cloud_should_be_indexed'] = should_be_indexed
    if not indexed and should_be_indexed:
        # Set the resources.hash to 'retry', so that the dataset will be re-processed within the next 10 minutes.
        dataset['resources.hash'] = ['retry']
    dataset['iati_cloud_removed_reason'] = dataset_indexing_result if not indexed else ""
    # If this is not an update but the file belongs to AIDA, mark it as managed from AIDA,
    # so in future updates the dataset will not be re-indexed, as it will automatically be updated from AIDA.
    if not update and "https://files.aida.tools" in dataset['resources'][0]['url']:
        dataset['iati_cloud_aida_sourced'] = True
    # Index the dataset metadata
    logging.info('-- Save the dataset metadata')
    result, should_retry = _index_dataset_metadata_to_dataset_core(dataset, draft, should_be_indexed, indexed)
    return dataset_indexing_result, result, should_retry


def _index_dataset_metadata_to_dataset_core(dataset, draft, should_be_indexed, indexed):
    # Remove any key/value pair if the key ends with ._
    dataset = {key: value for key, value in dataset.items() if not key.endswith('._')}

    if 'organization' in dataset and 'name' in dataset['organization']:
        solr_ds_url = settings.SOLR_DRAFT_DATASET_URL if draft else settings.SOLR_DATASET_URL
        result = index(
            f'iati-data-main/metadata/{dataset["organization"]["name"]}/{dataset["name"]}',
            dataset,
            solr_ds_url
        )
        should_retry = should_be_indexed and not indexed
    else:
        result = "The dataset does not contain proper organization metadata, therefore we cannot determine the organization name and source the datasets."  # NOQA: E501
        should_retry = False

    return result, should_retry


def _update_drop(update, draft, dataset):
    # drop the old data from solr
    if update:
        solr_cores = [settings.SOLR_ACTIVITY, settings.SOLR_BUDGET, settings.SOLR_RESULT, settings.SOLR_TRANSACTION]
        if draft:
            solr_cores += [settings.SOLR_DRAFT_ACTIVITY, settings.SOLR_DRAFT_BUDGET, settings.SOLR_DRAFT_RESULT,
                           settings.SOLR_DRAFT_TRANSACTION]
        for url in solr_cores:
            conn = Solr(url)
            conn.delete(q='%s:"%s"' % ('dataset.id', dataset['id']), commit=True)


def index_dataset(internal_url, dataset_filetype, codelist, currencies, dataset_metadata, draft=False):
    """
    Index the dataset to the correct core.

    :param internal_url: The internal url of the dataset.
    :param dataset_filetype: The filetype of the dataset.
    :param codelist: An initialized codelist object
    :param currencies: An initialized currencies object
    :return: true if indexing successful, false if failed. A message indicating the result
    """
    should_be_indexed = False
    try:
        if dataset_filetype == 'activity':
            core_url = settings.SOLR_ACTIVITY_URL if not draft else settings.SOLR_DRAFT_ACTIVITY_URL
        else:
            core_url = settings.SOLR_ORGANISATION_URL if not draft else settings.SOLR_DRAFT_ORGANISATION_URL
        json_path, should_be_indexed, p_res = convert_and_save_xml_to_processed_json(
            internal_url,
            dataset_filetype,
            codelist,
            currencies,
            dataset_metadata,
            draft
        )
        if json_path:
            result = index_to_core(core_url, json_path, remove=True)
            logging.info(f'result of indexing {result}')
            if result == 'Successfully indexed':
                return True, result, should_be_indexed
            return False, "Unable to index the processed dataset.", False
        return False, p_res, should_be_indexed
    except Exception as e:  # NOQA
        logging.warning(f'Exception occurred while indexing {dataset_filetype} dataset:\n{internal_url}\n{e}\nTherefore the dataset will not be indexed.')  # NOQA
        return False, f"An exception occurred while indexing, the dataset {'will be reindexed within 10 minutes.' if should_be_indexed else 'will not be indexed.'}", should_be_indexed


def convert_and_save_xml_to_processed_json(filepath, filetype, codelist, currencies, dataset_metadata, draft=False):
    """
    Read the XML into a convertible format and save it to a json file,
    after extracting the activity or organisations from it and cleaning the dataset.

    :param filepath: The filepath of the dataset.
    :param filetype: The filetype of the dataset.
    :param codelist: An initialized codelist object
    :param currencies: An initialized currencies object
    :param dataset_metadata: The metadata of the dataset.
    :return: The filepath of the json file.
    """
    should_be_indexed = False
    parser = ET.XMLParser(encoding='utf-8')
    try:
        etree = ET.parse(filepath, parser=parser)
        tree = ET.tostring(etree.getroot())
    except ET.ParseError:
        logging.info(f'-- Error parsing {filepath}')
        return None, should_be_indexed, "Unable to read XML file. It may have been accessible. Check the file source."
    # Convert the tree to json using BadgerFish method.
    data = bf.data(ET.fromstring(tree))
    # Retrieve activities
    data, data_found = extract_activity_or_organisation_data(filetype, data)

    if not data_found:
        logging.info(f'-- No data found in {filepath}')
        return data_found, should_be_indexed, "Data was not present in the data dump."
    # Clean the dataset
    data = recursive_attribute_cleaning(data)

    # Add our additional custom fields
    if filetype == 'activity':
        data, add_all_ok = custom_fields.add_all(data, codelist, currencies, dataset_metadata)
    if filetype == 'organisation':
        data = organisation_custom_fields.add_all(data)
    # if unable to add custom fields, do not save the dataset
    if not add_all_ok:
        return False, should_be_indexed, "Unable to add custom fields to the dataset, will be retried within the next 10 minutes."  # NOQA: E501

    json_path = json_filepath(filepath)
    if not json_path:
        logging.info(f'-- Error creating json path for {filepath}')
        return False, should_be_indexed, "A JSON path could not be created for the dataset."
    should_be_indexed = True
    logging.info(f'-- Saving to {json_path}')
    try:
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        logging.info(f'-- Error saving to {json_path}, failed')
        logging.error(f'Error writing to {json_path}: type: {type(e)} -- stack: {e}')
        return False, should_be_indexed, "Processed data could not be saved as JSON."

    if not settings.FCDO_INSTANCE:
        dataset_subtypes(filetype, data, json_path, draft)

    return json_path, should_be_indexed, "Success"


def extract_activity_or_organisation_data(filetype, data):
    data_found = False
    if filetype == 'activity' and 'iati-activities' in data:
        if 'iati-activity' in data['iati-activities']:
            data = data['iati-activities']['iati-activity']
            data_found = True
    elif filetype == 'organisation' and 'iati-organisations' in data:
        if 'iati-organisation' in data['iati-organisations']:
            data = data['iati-organisations']['iati-organisation']
            data_found = True
    return data, data_found


def json_filepath(filepath):
    """
    os.path provides the splitext function, which splits a
    path into (path, extension) and returns a tuple. Append .json to the path.

    :param filepath: The filepath of the dataset.
    :return: the filepath of the json file.
    """
    try:
        converted_path = ''.join((os.path.splitext(filepath)[0], '.json'))
        return converted_path
    except Exception:
        return False


def dataset_subtypes(filetype, data, json_path, draft=False):
    """
    extract and index the subtypes of the dataset if it is an activity dataset.

    :param filetype: The filetype of the dataset.
    :param data: The data of the dataset.
    :param json_path: The filepath of the json file.
    """
    # Activity subtypes
    subtypes = dict()
    if filetype == 'activity':
        for key in activity_subtypes.AVAILABLE_SUBTYPES:
            subtypes[key] = []

        subtypes = activity_subtypes.extract_all_subtypes(subtypes, data)
        index_subtypes(json_path, subtypes, draft)


def index_subtypes(json_path, subtypes, draft=False):
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
        try:
            try:
                with open(subtype_json_path, 'w') as json_file:
                    json.dump(subtypes[subtype], json_file)
            except Exception as e:
                logging.error(f'Error writing to {subtype_json_path}: type: {type(e)} -- stack: {e}')
                continue
            if draft:
                solr_url = activity_subtypes.AVAILABLE_DRAFT_SUBTYPES[subtype]
            else:
                solr_url = activity_subtypes.AVAILABLE_SUBTYPES[subtype]
            index_to_core(solr_url, subtype_json_path, remove=True)
        except Exception as e:
            logging.error(f'Error indexing subtype {subtype} of {json_path}:\n{e}')
