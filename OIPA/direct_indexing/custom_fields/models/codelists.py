from functools import lru_cache

from django.conf import settings
import requests
import json

# Original data source: https://codelists.codeforiati.org/api/
CODELIST_URL = 'https://codelists.codeforiati.org/api/json/en/'
USED_CODELISTS = [
    'AidType',
    'Country',
    'OrganisationType',
    'Region',
]
SOURCES = {}
for s in USED_CODELISTS:
    SOURCES[s] = f'{CODELIST_URL}{s}.json'


@lru_cache(maxsize=None)
class Codelists(object):
    """
    An object instantiating and containing the codelists
    """

    def __init__(self, download=False):
        self.codelists_dict = {}
        if download:
            self.download_codelists()
        else:
            self.read_codelists()
        
    def read_codelists(self):
        """
        Initialize the codelists by reading the listed json files and storing
        them in a dictionary.

        :return: None
        """
        path = settings.CODELISTS_JSON
        with open(path) as file:
            return json.load(file)


    def get_value(self, codelist_name, code, key='code', tbr='name'):
        """
        Code can be a single code, '11', or a list of codes, [11, 12].
        If code is a list, stringify and retrieve the value for each, otherwise
        return the value for the single code..

        :param codelist_name: The name of the codelist
        :param key: The key to retrieve the value from, default is 'code'.
        :param code: The code within the codelist, can be string or list.
        :param tbr: the field to be retrieved, for example 'name' or 'description', default is 'name'.
        :return: The content of the codelist at the given code, or a list of those values if the 'code' is a list
        """
        if codelist_name not in self.codelists_dict:
            return []
        codelist = self.codelists_dict[codelist_name]
        ret = []
        for item in codelist:
            if type(code) is list:
                for single_code in code:
                    if item[key] == str(single_code):  # Ensure code is string
                        ret.append(item[tbr])
            else:
                if item[key] == code:  # single codes are passed as string
                    return item[tbr]
        return ret
    
    def get_codelists(self):
        return self.codelists_dict

    def download_codelists(self):
        for key, value in SOURCES.items():
            r = requests.get(value)
            data = r.json()['data']
            self.codelists_dict[key] = data
        with open(settings.CODELISTS_JSON, 'w') as file:
            json.dump(self.codelists_dict, file)
