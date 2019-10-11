import urllib
import json
from OIPA import settings
import os


class PostmanAPIImport(object):
    fields_to_remove = ["event", "response"]
    file_path = os.environ.get(
        'OIPA_STATIC_ROOT',
    os.path.join(
        os.path.dirname(settings.BASE_DIR),
        'public/static'))

    def get_json(self):

        request = urllib.request.Request(
            "https://api.getpostman.com/collections/7423966-c07eebd3-61b2-47b4-9bfd-1bac7ec96c9f",
            headers={"x-Api-Key": "55dfaaebcc9448bba40e5ff485305a2b"})
        response = urllib.request.urlopen(request)
        json_string = response.read()
        result = json.loads(json_string)
        self.simplify(result)
        with open(self.file_path + '/postman/postman_json.json', 'w') as outfile:
            json.dump(result, outfile)

    def simplify(self, full_json):
        self.remove_fields(full_json['collection'])
        self.recursive_clean(full_json['collection']['item'])

    def remove_fields(self, before_remove_event):
        for fields in self.fields_to_remove:
            if fields in before_remove_event:
                del before_remove_event[fields]

    def recursive_clean(self, before_remove_response):
        for item in before_remove_response:
            self.remove_fields(item)
            if 'item' in item:
                self.recursive_clean(item['item'])



