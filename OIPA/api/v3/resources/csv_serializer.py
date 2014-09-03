import csv
import StringIO
from tastypie.serializers import Serializer


class CsvSerializer(Serializer):
    formats = ['json', 'xml', 'csv']
    content_types = {
        'json': 'application/json',
        'xml': 'application/xml',
        'csv': 'text/csv',
    }


    def to_csv(self, data, options=None):
        options = options or {}

        data = self.to_simple(data, options)

        raw_data = StringIO.StringIO()
        first = True

        if "meta" in data.keys():#if multiple objects are returned
            objects = data.get("objects")

            for value in objects:

                test = {}

                self.set_data(value, test)

                # self.flatten("", value, test)
                if first:
                    writer = csv.DictWriter(raw_data, test.keys(), quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                    writer.writeheader()
                    writer.writerow(test)
                    first=False
                else:
                    writer.writerow(test)
        else:
            test = {}
            self.flatten("", data, test)
            if first:
                writer = csv.DictWriter(raw_data, test.keys(), quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                writer.writerow(test)
                first=False
            else:
                writer.writerow(test)
        CSVContent=raw_data.getvalue()
        return CSVContent

    def set_data(self, data, column_dict={}):

        # set keys
        column_dict = {'activity_scope': None, 'activity_status': None, 'budget': None, 'collaboration_type': None, 'countries': None, 'default_aid_type': None, 'default_finance_type': None, 'default_flow_type': None, 'descriptions': None, 'titles': None, 'documents': None, 'end_actual': None, 'end_planned': None, 'start_actual': None, 'start_planned': None, 'iati_identifier': None, 'last_updated_datetime': None, 'participating_organisations': None, '': None}

        # fill keys



        if "meta" in data.keys():

            for item in data["activity_scope"]:

                column_dict["activity_scope"] = None

            for item in data["meta"]:

                column_dict["meta"] = None

        return "Columnized data"


    def flatten(self, parent_name, data, odict={}):
        # if list, flatten the list
        if isinstance(data, list):
            for value in data:
                self.flatten(parent_name, value, odict)
        # if dictionary, flatten the dictionary
        elif isinstance(data, dict):
            for (key, value) in data.items():
                # if no dict or list, add to odict
                if not isinstance(value, (dict, list)):
                    if parent_name:
                        key = parent_name + "_" + key
                    odict[key] = value
                else:
                    self.flatten(key, value, odict)