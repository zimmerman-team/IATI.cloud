import csv
import StringIO

from tastypie.serializers import Serializer

class CsvHelper(Serializer):
    formats = ['json', 'xml', 'csv']
    content_types = {
        'json': 'application/json',
        'xml': 'application/xml',
        'csv': 'text/csv',
    }


    def to_csv(self, data, options=None):
        try:
            options = options or {}
            data = self.to_simple(data, options)

            raw_data = StringIO.StringIO()
            first = True

            if "meta" in data.keys():#if multiple objects are returned
                objects = data.get("objects")

                for value in objects:

                    test = {}
                    self.flatten("", value, test)
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
        except Exception as e:
            print e
            return None

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
                    value = unicode(value)
                    odict[key] = value.encode('utf-8', 'ignore')
                else:
                    self.flatten(key, value, odict)