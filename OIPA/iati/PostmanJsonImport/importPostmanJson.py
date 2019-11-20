import json
import os
import urllib
from datetime import datetime

from OIPA import settings


class PostmanAPIImport(object):
    fields_to_remove = ["event", "response"]
    file_path = os.environ.get(
        'OIPA_STATIC_ROOT',
        os.path.join(
            os.path.dirname(settings.BASE_DIR),
            'public/static'))

    def get_json(self):

        request = urllib.request.Request(
            "https://api.getpostman.com/collections/7423966-c07eebd3-61b2-47b4-9bfd-1bac7ec96c9f",     # NOQA: E501
            headers={"x-Api-Key": "55dfaaebcc9448bba40e5ff485305a2b"})
        response = urllib.request.urlopen(request)
        json_string = response.read()
        result_for_test_datastore_iatistandard_org = json.loads(json_string)
        result_for_iati_cloud = json.loads(json_string)

        self.simplify(result_for_iati_cloud, 'iati.cloud')
        self.simplify(result_for_test_datastore_iatistandard_org, 'test-datastore.iatistandard.org')
        try:
            with open(self.file_path + '/postman/postman_json_iati_cloud.json', 'w') as outfile:     # NOQA: E501
                json.dump(result_for_iati_cloud, outfile)
            print("Postman json file for iati.cloud was created on: ", datetime.now())

            with open(self.file_path + '/postman/postman_json_test_datastore_iatistandard_org.json',
                      'w') as outfile:     # NOQA: E501
                json.dump(result_for_test_datastore_iatistandard_org, outfile)
            print("Postman json file for test-datastore.iatistandard.org was created on: ", datetime.now())
        except IOError:
            pass

    def simplify(self, full_json, url_string_to_replace_with):
        self.remove_fields(full_json['collection'], url_string_to_replace_with)
        self.recursive_clean(full_json['collection']['item'], url_string_to_replace_with)

    def remove_fields(self, before_remove_event, url_string_to_replace_with):
        for fields in self.fields_to_remove:
            if fields in before_remove_event:
                del before_remove_event[fields]
            if 'request' in before_remove_event:
                self.url_replacing(before_remove_event, url_string_to_replace_with)

    def recursive_clean(self, before_remove_response, url_string_to_replace_with):
        for item in before_remove_response:
            self.remove_fields(item, url_string_to_replace_with)
            if 'item' in item:
                self.recursive_clean(item['item'], url_string_to_replace_with)

    def url_replacing(self, element_string_to_be_replaced, url_string_to_replace_with):
        new_url = element_string_to_be_replaced['request']['url']['raw'].replace('iati.cloud', url_string_to_replace_with)  # NOQA: E501
        element_string_to_be_replaced['request']['url']['raw'] = new_url
