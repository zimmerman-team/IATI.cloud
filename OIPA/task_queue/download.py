
import celery
import errno
import logging
import os
import urllib

from django.conf import settings

from iati_synchroniser.models import Dataset, Publisher, filetype_choices


# Get an instance of a logger
logger = logging.getLogger(__name__)


class DatasetDownloadTask(celery.Task):
    """
    Dataset Download Task
    Use:
    task = DatasetDownloadTask()
    task.apply_async(dataset_id=1)
    """
    # Assigned the default of retry task if get exception
    autoretry_for = (Exception, )
    retry_kwargs = {
        'max_retries': settings.VALIDATION.get(
            'api'
        ).get('retry').get('max_retries')
    }
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False
    # Local variables

    _dataset = Dataset
    is_download_datasets = False


    def run(self, dataset_data, *args, **kwargs):
        """Run the dataset download task"""

        if self.is_download_datasets and settings.DOWNLOAD_DATASETS:
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
            # if '.xml' not in filename:
            #    filename += '.xml'
            # This is not sufficient as some urls sometime already have a
            # .xml at the wrong place for example :
            # http://iati.cloud/static/datasets/BE-BCE_KBO-0410644946/Activity/2.02/activities.xml?id=29&hash=a77d969b23e706cb8fec1850daae34e9 # NOQA: E501
            if not filename.endswith('.xml'):
                filename = filename.replace('.xml', '')
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




