import json
import models
import httplib
import urllib2
import datetime
from iati.models import OrganisationIdentifier
from iati_synchroniser.exception_handler import exception_handler


IATI_URL = 'http://www.iatiregistry.org/api/search/dataset?{options}'


class DatasetSyncer():
    # TODO: Clean unnecessary exception catchers.
    def __init__(self):
        """
        Prefetch data, to minify amount of DB queries
        """
        self.source_urls = set([xmlsource['source_url'] for xmlsource in models.IatiXmlSource.objects.values('source_url')])
        self.publisher_ids = set([publisher['org_id'] for publisher in models.Publisher.objects.values('org_id')])
        self.organisation_identifiers = set([org['code'] for org in OrganisationIdentifier.objects.values('code')])

    def synchronize_with_iati_api(self, data_type, extra_options=[]):
        """
        Start looping through the datasets
        """
        url_options = [
            'extras_filetype=activity',
            'all_fields=1',
            'limit=200',
        ]
        url_options.extend(extra_options)

        if data_type == 2:
            url_options[0] = 'extras_filetype=organisation'

        for i in range(0, 10000, 200):
            options = '&'.join(url_options + ['offset={}'.format(i)])
            page_url = IATI_URL.format(options=options)
            if not self.synchronize_with_iati_api_by_page(page_url, data_type):
                break

    def synchronize_with_iati_api_by_page(self, url, data_type, try_number=0):
        """
        Loop through the datasets by page
        """
        # TODO: Clean this function
        try:
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json_objects = json.load(f)

            if json_objects is not None:
                if len(json_objects['results']):
                    # For each dataset object
                    for line in json_objects['results']:
                        try:
                            self.parse_json_line(line, data_type)
                        except Exception as e:
                            exception_handler(
                                e,
                                'synchronize_with_iati_api_by_page',
                                "Unexpected error")
                    return True
                else:
                    return False

        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException), e:
            exception_handler(e, "HTTP error", url)

            if try_number < 4:
                self.synchronize_with_iati_api_by_page(
                    url,
                    data_type,
                    try_number + 1)
            else:
                return False

    def update_publisher(self, iati_id, abbreviation, name):

        if iati_id in self.publisher_ids and iati_id != 'Unknown':
            current_publisher = models.Publisher \
                .objects.get(org_id=iati_id)
        else:
            if iati_id in self.organisation_identifiers:
                current_publisher_meta = OrganisationIdentifier \
                    .objects.get(code=iati_id)
                abbreviation = current_publisher_meta.abbreviation

            current_publisher = self.add_publisher_to_db(
                iati_id, abbreviation, name)

            self.publisher_ids.add(iati_id)

        return current_publisher

    def add_publisher_to_db(self,
                            org_id,
                            org_abbreviate_value,
                            org_name_value):
        new_publisher = models.Publisher(
            org_id=org_id,
            org_abbreviate=org_abbreviate_value,
            org_name=org_name_value,
            default_interval='MONTHLY')
        new_publisher.save()
        return new_publisher

    def add_iati_xml_source_to_db(self,
                                  url,
                                  title,
                                  name,
                                  current_publisher,
                                  cur_type):
        new_source = models.IatiXmlSource(
            ref=name,
            title=title,
            publisher=current_publisher,
            source_url=url,
            type=cur_type)
        new_source.save(process=False, added_manually=False)
        return new_source

    def parse_json_line(self, line, data_type):
        """
        Parse line from IATI response
        """
        try:
            publisher_iati_id = line['extras']['publisher_iati_id']
        except KeyError:
            publisher_iati_id = None

        publisher_abbreviation = ''
        publisher_name = 'Unknown'
        try:
            source_url = str(line['res_url'][0]).replace(' ', '%20')
        except IndexError:
            source_url = ''
        source_name = line.get('name', '')
        source_title = line.get('title', '')

        try:
            data_dict = json.loads(line.get('data_dict', ''))
            publisher_name = data_dict['organization']['title']
        except (ValueError, KeyError):
            pass
        except Exception as e:
            msg = ("Unexpected error in synchronize_with_iati_api_by_page "
                   "organisation match:")
            exception_handler(e, 'synchronize_with_iati_api_by_page', msg)

        if source_url not in self.source_urls:

            if publisher_iati_id:
                current_publisher = self.update_publisher(
                    publisher_iati_id,
                    publisher_abbreviation,
                    publisher_name)
            else:
                current_publisher = self.add_publisher_to_db(
                    'Unknown',
                    publisher_abbreviation,
                    publisher_name)

            self.add_iati_xml_source_to_db(
                source_url,
                source_title,
                source_name,
                current_publisher,
                data_type)

            self.source_urls.add(source_url)

        else:
            msg = "Updated publisher and last found in registry on: "
            exception_handler(None, msg, source_url)

            source = models.IatiXmlSource.objects.get(source_url=source_url)
            source.last_found_in_registry = datetime.datetime.now()

            if source.publisher.org_id != publisher_iati_id:
                new_publisher = self.update_publisher(
                    publisher_iati_id,
                    publisher_abbreviation,
                    publisher_name)
                source.publisher = new_publisher
            source.save(process=False, added_manually=False)

