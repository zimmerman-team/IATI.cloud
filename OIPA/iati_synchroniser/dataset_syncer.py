import datetime
import hashlib
import json
import logging
import ssl
import urllib

import requests
from django.utils.encoding import smart_text

from iati_organisation.models import Organisation
from iati_synchroniser.create_publisher_organisation import (
    create_publisher_organisation
)
from iati_synchroniser.models import Dataset, Publisher
from task_queue.tasks import DatasetDownloadTask, DatasetValidationTask

DATASET_URL = 'https://iatiregistry.org/api/action/package_search?rows=200&{options}'  # NOQA: E501
PUBLISHER_URL = 'https://iatiregistry.org/api/action/organization_list?all_fields=true&include_extras=true&limit=200&{options}'  # NOQA: E501

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DatasetSyncer(object):
    is_download_datasets = False

    def get_data(self, url):
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        json_objects = json.loads(response.decode('utf-8'))
        return json_objects

    def get_val_in_list_of_dicts(self, key, dicts):
        return next(
            (item for item in dicts
                if item.get("key") and item["key"] == key), None
        )

    def synchronize_with_iati_api(self, is_download_datasets=False):
        """
        First update all publishers.
        Then all datasets.
        """

        self.is_download_datasets = is_download_datasets

        # parse publishers
        offset = 0

        while True:
            # get data
            options = 'offset={}'.format(offset)
            offset += 200
            page_url = PUBLISHER_URL.format(options=options)
            results = self.get_data(page_url)

            for publisher in results['result']:
                self.update_or_create_publisher(publisher)
            # check if done
            if len(results['result']) == 0:
                break

        # parse datasets
        offset = 0

        while True:
            # get data
            options = 'start={}'.format(offset)
            offset += 200
            page_url = DATASET_URL.format(options=options)
            results = self.get_data(page_url)

            # do not verify SSL (for downloading dataset):
            ssl._create_default_https_context = ssl._create_unverified_context

            # update dataset
            for dataset in results['result']['results']:
                self.update_or_create_dataset(dataset)

            # check if done
            if len(results['result']['results']) == 0:
                break

        # remove deprecated publishers / datasets
        # self.remove_deprecated()

    def get_iati_version(self, dataset_data):

        iati_version = self.get_val_in_list_of_dicts(
            'iati_version', dataset_data['extras'])
        if iati_version:
            iati_version = iati_version.get('value')
        else:
            iati_version = ''

        return iati_version

    def update_or_create_publisher(self, publisher):
        """

        """
        if publisher['package_count'] == 0:
            package_count = None
        else:
            package_count = publisher['package_count']

        obj, created = Publisher.objects.update_or_create(
            iati_id=publisher['id'],
            defaults={
                'publisher_iati_id': publisher['publisher_iati_id'],
                'name': publisher['name'],
                'display_name': publisher['title'],
                'package_count': package_count,
            }
        )

        if not Organisation.objects.filter(
                organisation_identifier=publisher[
                    'publisher_iati_id'
                ]).exists():
            create_publisher_organisation(
                obj,
                publisher['publisher_organization_type']
            )

        return obj

    def get_dataset_filetype(self, dataset_data):
        filetype_name = self.get_val_in_list_of_dicts(
            'filetype', dataset_data['extras'])

        if filetype_name and filetype_name.get('value') == 'organisation':
            filetype = 2
        else:
            filetype = 1

        return filetype

    def update_or_create_dataset(self, dataset):
        """
        Updates or creates a Dataset AND downloads it locally. Returns internal
        URL for the Dataset

        """

        filetype = self.get_dataset_filetype(dataset)

        iati_version = self.get_iati_version(dataset)

        # trololo edge cases
        if not len(dataset['resources']) or not dataset['organization']:
            return

        publisher = Publisher.objects.get(
            iati_id=dataset['organization']['id'])
        sync_sha1 = ''
        source_url = dataset['resources'][0]['url']
        response = None
        try:
            response = requests.get(source_url)
        except requests.exceptions.SSLError:
            response = requests.get(source_url, verify=False)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
            pass

        if response and response.status_code == 200:
            try:
                iati_file = smart_text(response.content, 'utf-8')
            # XXX: some files contain non utf-8 characters:
            # FIXME: this is hardcoded:
            except UnicodeDecodeError:
                iati_file = smart_text(response.content, 'latin-1')

            # 2. Encode the string to use for hashing:
            hasher = hashlib.sha1()
            hasher.update(iati_file.encode('utf-8'))
            sync_sha1 = hasher.hexdigest()

        obj, created = Dataset.objects.update_or_create(
            iati_id=dataset['id'],
            defaults={
                'name': dataset['name'],
                'title': dataset['title'][0:254],
                'filetype': filetype,
                'publisher': publisher,
                'source_url': dataset['resources'][0]['url'],
                'iati_version': iati_version,
                'last_found_in_registry': datetime.datetime.now(),
                'added_manually': False,
                'date_created': dataset['metadata_created'],
                'date_updated': dataset['metadata_modified'],
                'sync_sha1': sync_sha1
            }
        )
        # this also returns internal URL for the Dataset:
        return_value = DatasetDownloadTask.delay(dataset_data=dataset)
        obj.internal_url = return_value.get(disable_sync_subtasks=False) or ''
        obj.save()

        # Validation dataset with the current. we don't do validation for
        # the moment
        DatasetValidationTask.delay(dataset_id=obj.id)

    def remove_deprecated(self):
        """
        remove old publishers and datasets that used an id between 1-5000
        instead of the IATI Registry UUID (thats way over string length 5,
        pretty hacky code here tbh but its a one time solution)
        """
        for p in Publisher.objects.all():
            if len(p.iati_id) < 5:
                p.delete()

        for d in Dataset.objects.all():
            if len(p.iati_id) < 5:
                p.delete()
