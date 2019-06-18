import datetime
import errno
import json
import os
import ssl
import urllib

from django.conf import settings

from iati_organisation.models import Organisation
from iati_synchroniser.create_publisher_organisation import (
    create_publisher_organisation
)
from iati_synchroniser.models import Dataset, Publisher, filetype_choices

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

            # do not verify SSL (for downloading dataset):
            ssl._create_default_https_context = ssl._create_unverified_context

            # update dataset
            for dataset in results['result']['results']:
                self.update_or_create_dataset(dataset)

            # check if done
            if len(results['result']['results']) == 0:
                break

        # remove deprecated publishers / datasets
        self.remove_deprecated()

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

        # this also returns internal URL for the Dataset:
        obj.internal_url = self.download_dataset(dataset) or ''
        obj.save()

    def download_dataset(self, dataset_data):
        """Based on dataset URL, downloads and saves it in the server

        TODO: create error log (DatasetNote) object if the URL is not
        reachable (requires broader implementation of error logs)
        """

        if settings.DOWNLOAD_DATASETS:

            # URL:
            dataset_url = dataset_data['resources'][0]['url']

            # IATI_VERSION:
            iati_version = self.get_iati_version(dataset_data)

            # PUBLISHER_IATI_ID:
            publisher_iati_id = self.get_val_in_list_of_dicts(
                'publisher_iati_id',
                dataset_data['extras']
            ).get('value')

            # FILETYPE:
            filetype = self.get_dataset_filetype(dataset_data)
            normalized_filetype = dict(filetype_choices)[filetype]

            # DOWNLOAD files directly to the static dir (so they're served
            # directly w/o Django's 'colectstatic' command):
            static_dir = settings.STATIC_ROOT

            filename = dataset_url.split('/')[-1]

            # sometimes URL is not 'example.com/blah.xml':
            if '.xml' not in filename:
                filename += '.xml'

            if '/' in publisher_iati_id:
                publisher_iati_id = publisher_iati_id.replace('/', '-')

            # Download directory without prepending path from root dir to
            # static folder:
            main_download_dir = os.path.join(
                'datasets',
                publisher_iati_id,
                normalized_filetype,
                iati_version
            )

            # Full directory from root till folder (w/o file name):
            full_download_dir = os.path.join(
                static_dir,
                main_download_dir
            )

            if not os.path.exists(full_download_dir):
                os.makedirs(full_download_dir, exist_ok=True)
                try:
                    os.makedirs(main_download_dir)

                # The reason to add the try-except block is to handle the
                # case when the directory was created between the
                # os.path.exists and the os.makedirs calls, so that to
                # protect us from race conditions:
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise

            # Full directory from root to filename:
            download_dir_with_filename = os.path.join(
                full_download_dir,
                filename
            )

            try:
                urllib.request.urlretrieve(
                    dataset_url,
                    download_dir_with_filename
                )
            except (
                urllib.request.HTTPError,  # 403
                urllib.request.URLError,  # timeouts
                ConnectionResetError,
            ):
                pass

            # URL string to save as a Dataset attribute:
            return os.path.join(main_download_dir, filename)

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
