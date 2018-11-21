import datetime
import json
import urllib

from iati_organisation.models import Organisation
from iati_synchroniser.create_publisher_organisation import (
    create_publisher_organisation
)
from iati_synchroniser.models import Dataset, Publisher

DATASET_URL = 'https://iatiregistry.org/api/action/package_search?rows=200&{options}'  # NOQA: E501
PUBLISHER_URL = 'https://iatiregistry.org/api/action/organization_list?all_fields=true&include_extras=true&limit=200&{options}'  # NOQA: E501


class DatasetSyncer():

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

    def synchronize_with_iati_api(self):
        """
        First update all publishers.
        Then all datasets.
        """

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
            # update dataset
            for dataset in results['result']['results']:
                self.update_or_create_dataset(dataset)
            # check if done
            if len(results['result']['results']) == 0:
                break

        # remove deprecated publishers / datasets
        self.remove_deprecated()

    def update_or_create_publisher(self, publisher):
        """

        """
        obj, created = Publisher.objects.update_or_create(
            iati_id=publisher['id'],
            defaults={
                'publisher_iati_id': publisher['publisher_iati_id'],
                'name': publisher['name'],
                'display_name': publisher['title']
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

        """
        filetype_name = self.get_val_in_list_of_dicts(
            'filetype', dataset['extras'])

        if filetype_name and filetype_name.get('value') == 'organisation':
            filetype = 2
        else:
            filetype = 1

        iati_version = self.get_val_in_list_of_dicts(
            'iati_version', dataset['extras'])
        if iati_version:
            iati_version = iati_version.get('value')
        else:
            iati_version = ''

        # trololo edge cases
        if not len(dataset['resources']) or not dataset['organization']:
            return

        publisher = Publisher.objects.get(
            iati_id=dataset['organization']['id'])

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
                'added_manually': False
            }
        )

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
