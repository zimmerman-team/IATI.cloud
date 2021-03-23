import datetime
import json
import logging
import ssl
import urllib

from iati_organisation.models import Organisation
from iati_synchroniser.create_publisher_organisation import (
    create_publisher_organisation
)
from iati_synchroniser.models import Dataset, DatasetUpdateDates, Publisher
from task_queue.tasks import DatasetDownloadTask

DATASET_URL = 'https://iatiregistry.org/api/action/package_search?rows=200&{options}'  # NOQA: E501
PUBLISHER_URL = 'https://iatiregistry.org/api/action/organization_list?all_fields=true&include_extras=true&limit=50&{options}'  # NOQA: E501

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
            offset += 50
            page_url = PUBLISHER_URL.format(options=options)
            results = self.get_data(page_url)

            for publisher in results['result']:
                self.update_or_create_publisher(publisher)
            # check if done
            if len(results['result']) == 0:
                break

        # parse datasets
        offset = 0

        dataset_sync_start = datetime.datetime.now()
        DatasetUpdateDates.objects.create(
            timestamp=dataset_sync_start,
            success=False
        )

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

        dud = DatasetUpdateDates.objects.last()
        dud.success = True
        dud.save()

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

    def update_or_create_dataset(self, dataset):
        """
        Updates or creates a Dataset AND downloads it locally. Returns internal
        URL for the Dataset

        """

        # edge cases
        if not len(dataset['resources']) or not dataset['organization']:
            return

        # Pass the data generated here to the
        DatasetDownloadTask.delay(dataset_data=dataset)

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
