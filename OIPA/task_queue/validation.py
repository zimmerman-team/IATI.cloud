import hashlib
import io
# import the logging library
import logging
import time

import celery
import requests
from django.conf import settings
from requests.exceptions import RequestException

from iati_synchroniser.models import Dataset

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DatasetValidationTask(celery.Task):
    """
    Dataset Validation Task
    Use:
    task = DatasetValidationTask()
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
    _root_validation_url = '{host}{root}{version}'.format(
        host=settings.VALIDATION.get('host'),
        root=settings.VALIDATION.get('api').get('root'),
        version=settings.VALIDATION.get('api').get('version')
    )
    _dataset = Dataset
    _validation_id = None
    _file_id = None
    _json_result = None
    _validation_md5 = None

    def run(self, dataset_id=None, *args, **kwargs):
        """Run the dataset validation task"""
        self._dataset = Dataset.objects.get(id=dataset_id)

        if self._check():
            self._updated()

        # We don't do ad-hoc validation anymore
        # else:
        #     # Upload file
        #     self._post()
        #     # Continue validation if validation id is not none
        #     if self._validation_id:
        #         # Begin validation
        #         self._start()
        #         # Process validation
        #         self._process()
        #         # If the variable file id is not None,
        #         # that mean the process can continue
        #         if self._file_id:
        #             # Get JSON result of the current validation
        #             self._get(ad_hoc=True)
        #             # If the JSON result is not None then update
        #             # the current dataset
        #             if self._json_result:
        #                 self._updated()

    def _check(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X '
                                 '10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}  # NOQA: E501

        try:
            response = requests.get(self._dataset.source_url, headers=headers,
                                    timeout=30)
        except requests.exceptions.SSLError:
            try:
                response = requests.get(self._dataset.source_url, verify=False,
                                        headers=headers, timeout=30)
            except (requests.exceptions.SSLError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.TooManyRedirects,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ChunkedEncodingError,
                    ) as e:
                logger.error(e)
                return False
        except requests.exceptions.Timeout:
            try:
                response = requests.get(self._dataset.source_url, timeout=30)
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.TooManyRedirects,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ChunkedEncodingError,
                    ) as e:
                logger.error(e)
                return False
        except (requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ChunkedEncodingError,
                ) as e:
            logger.error(e)
            return False

        if response.status_code == 200:
            md5 = hashlib.md5()
            md5.update(response.content)
            self._validation_md5 = md5.hexdigest()
            self._file_id = self._validation_md5 + '.xml'
            self._get(ad_hoc=False)
            if self._json_result:
                return True

    def _post(self):
        """Send XML file to the third party validation"""
        try:
            # Get file from the url of the dataset
            get_response = requests.get(self._dataset.source_url)
            # Continue if status is OK
            if get_response.status_code == 200:
                # Assign file from the content response
                file = io.BytesIO(get_response.content)
                # Add the default filename to the file
                file.name = 'dataset.xml'
                # Make dict files
                files = {'file': file}
                # POST request with the parameters for upload
                post_file_url = '{}{}'.format(
                    self._root_validation_url,
                    settings.VALIDATION.get('api').get('urls').get('post_file')
                )
                # Upload the file
                post_response = requests.post(
                    post_file_url,
                    files=files
                )
                # If response if OK then assigned the validation id
                if post_response.status_code == 200:
                    # Get the Sha512 of the current XML and save to dataset.
                    # This will use to compare the Sha512 with the source XML.
                    # So when the XML which has valid status ("success")
                    # will be parsing, we should compare the Sha512 of the XML
                    # and with this Sha512.
                    hashlib_md5 = hashlib.md5()
                    hashlib_md5.update(get_response.content)
                    self._validation_md5 = hashlib_md5.hexdigest()
                    # Update validation id for the next process
                    self._validation_id = post_response.json().get('id', None)

        except requests.exceptions.SSLError as e:
            logger.info('%s (%s)' % (e, type(e)) + self._dataset.source_url)
            try:
                resp = requests.get(self._dataset.source_url, verify=False)
                if resp.status_code == 200:
                    file = io.BytesIO(resp.content)
                    file.name = 'dataset.xml'
                    files = {'file': file}
                    post_file_url = '{}{}'.format(
                        self._root_validation_url,
                        settings.VALIDATION.get('api').get('urls')
                            .get('post_file')
                    )
                    post_response = requests.post(
                        post_file_url,
                        files=files
                    )
                    if post_response.status_code == 200:
                        hashlib_md5 = hashlib.md5()
                        hashlib_md5.update(resp.content)
                        self._validation_md5 = hashlib_md5.hexdigest()
                        self._validation_id = post_response.json()\
                            .get('id', None)

            except Exception as e:
                logger.error(e)

        except RequestException as e:
            logger.error(e)

    def _start(self):
        """Start the validation"""
        # Format the URL of the start validation
        # Please check settings.VALIDATION
        start_validation_url = '{}{}'.format(
            self._root_validation_url,
            settings.VALIDATION.get('api').get(
                'urls'
            ).get('start_validation').format(
                validation_id=self._validation_id
            )
        )
        # Request to the API to run validation of the current dataset
        requests.get(start_validation_url)

    def _process(self):
        """
        Check status of the running validation.
        If validation is done the get a JSON result
        from the third party validation
        and save the feedback ruleset to the dataset.
        This will be looping until the process validation is done.
        """
        # The process of the validation URL is the same with
        # the start validation, this is a bit confused.
        process_validation_url = '{}{}'.format(
            self._root_validation_url,
            settings.VALIDATION.get('api').get(
                'urls'
            ).get('start_validation').format(validation_id=self._validation_id)
        )
        # Get a sleep in the seconds for the global settings
        sleep_second_process = settings.VALIDATION.get('api').get(
            'sleep_second_process'
        )
        # If not yet done, the bellow looping should be continue
        max_loop_process = settings.VALIDATION.get(
            'api'
        ).get('max_loop_process')
        loop = 0
        while loop < max_loop_process:
            # Incr loop
            loop += 1
            # Get response process
            response = requests.get(process_validation_url)

            # Sleep in the seconds
            time.sleep(sleep_second_process)
            # If response status is 200, then continue
            if response.status_code == 200:
                # If response has field 'json-updated'
                # that mean the process is done
                if response.json().get('json-updated', None):
                    loop = max_loop_process
                    # Assign file_id form the response
                    # to get a JSON file in the process
                    self._file_id = response.json().get('fileid')
            else:
                # Looping is done and cancel the process validation of
                # the current dataset
                response = requests.get(process_validation_url, verify=False)
                if response.status_code == 200:
                    if response.json().get('json-updated', None):
                        loop = max_loop_process
                        self._file_id = response.json().get('fileid')
                else:
                    loop = max_loop_process

    def _get(self, ad_hoc=False):
        """Get the JSON result of the validation to get a feedback ruleset"""
        # The default of the file id extension to json
        json_file = self._file_id.replace('xml', 'json')
        # Format the get json file ur
        if ad_hoc:
            get_json_file_url = '{}{}'.format(
                self._root_validation_url,
                settings.VALIDATION.get('api').get(
                    'urls'
                ).get('get_json_file_ad_hoc').format(json_file=json_file)
            )
        else:
            get_json_file_url = '{}{}'.format(
                self._root_validation_url,
                settings.VALIDATION.get('api').get(
                    'urls'
                ).get('get_json_file').format(json_file=json_file)
            )
        # Request to the JSON result to the server
        response = requests.get(get_json_file_url, timeout=30)
        # If the response if OK then save the result
        # to the variable json result
        if response.status_code == 200:
            self._json_result = response.json()
        else:
            response = requests.get(get_json_file_url, verify=False, timeout=30)  # NOQA: E501
            if response.status_code == 200:
                self._json_result = response.json()

    def _updated(self):
        """
        Update the current dataset to save a feedback ruleset
        then we can use this the value of the feedback ruleset
        to control the current dataset is ready to parsing
        if the value is 'success'
        """
        # Get all severity value and put them in the array
        summary = self._json_result.get('summary', None)
        # Set valid status from settings
        # Be carefully to get valid status from settings,
        # please coordinate with a programmer of third party validation
        # to set value of the valid status
        # valid_status = settings.VALIDATION.get('api').get('valid_status')
        # Initial validation status
        # validation_status = None

        # Make value in he unique array and get a valid status
        # And set a validation_status to the valid status or not.
        # If one of the severities in the array has valid status, that means
        # the current dataset is valid.

        # unique_severities = list(set(summary))
        # for severity in unique_severities:
        #     # If the validation status has assigned as a valid status,
        #     # then not possible to change to others status.
        #     if validation_status != valid_status and severity ==
        #     valid_status:
        #         validation_status = severity
        #     elif validation_status != valid_status and \
        #             severity != valid_status:
        #         validation_status = severity

        # If success the save the Sha512 of the current validation
        # if validation_status == valid_status:
        self._dataset.validation_md5 = self._validation_md5

        # Save validation status to the dataset.
        self._dataset.validation_status = summary
        self._dataset.save()
