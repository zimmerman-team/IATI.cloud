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
            headers={"x-Api-Key": "PMAK-6078132671bad90052a5e3c3-da2fb4b9a5279d26a0fc7104c7d3aef61f"})  # NOQA: E501
        response = urllib.request.urlopen(request)
        json_string = response.read()
        result_for_test_datastore_iatistandard_org = json.loads(json_string.decode('utf-8-sig'))  # NOQA: E501
        result_for_iati_cloud = json.loads(json_string.decode('utf-8-sig'))

        self.simplify(result_for_iati_cloud, 'iatidatastore.iatistandard.org')
        self.simplify(result_for_test_datastore_iatistandard_org, 'test-datastore.iatistandard.org')  # NOQA: E501
        try:
            with open(self.file_path + '/postman/postman_json_iati_cloud.json', 'w') as outfile:     # NOQA: E501
                json.dump(result_for_iati_cloud, outfile)
            print("Postman json file for iati.cloud was created on: ", datetime.now())  # NOQA: E501

            with open(self.file_path + '/postman/postman_json_test_datastore_iatistandard_org.json',  # NOQA: E501
                      'w') as outfile:     # NOQA: E501
                json.dump(result_for_test_datastore_iatistandard_org, outfile)
            print("Postman json file for test-datastore.iatistandard.org was created on: ", datetime.now())  # NOQA:E501
        except IOError:
            pass

    def simplify(self, full_json, url_string_to_replace_with):
        self.remove_fields(full_json['collection'], url_string_to_replace_with)
        self.recursive_clean(full_json['collection']['item'], url_string_to_replace_with)  # NOQA: E501

    def remove_fields(self, before_remove_event, url_string_to_replace_with):
        for fields in self.fields_to_remove:
            if fields in before_remove_event:
                del before_remove_event[fields]
            if 'request' in before_remove_event:
                self.url_replacing(before_remove_event, url_string_to_replace_with)  # NOQA: E501

    def recursive_clean(self, before_remove_response, url_string_to_replace_with):  # NOQA: E501
        for item in before_remove_response:
            self.remove_fields(item, url_string_to_replace_with)
            if 'item' in item:
                self.recursive_clean(item['item'], url_string_to_replace_with)

    @staticmethod
    def url_replacing(element_string_to_be_replaced, url_string_to_replace_with):  # NOQA: E501
        new_url = element_string_to_be_replaced['request']['url']['raw'].replace('iati.cloud', url_string_to_replace_with)  # NOQA: E501
        element_string_to_be_replaced['request']['url']['raw'] = new_url
