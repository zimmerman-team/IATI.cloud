import csv
import StringIO
from tastypie.serializers import Serializer


class CSVSerializer(Serializer):
    formats = ['json', 'jsonp', 'xml', 'yaml', 'html', 'csv']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'xml': 'application/xml',
        'yaml': 'text/yaml',
        'html': 'text/html',
        'csv': 'text/csv',
    }

    def to_csv(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        raw_data = StringIO.StringIO()
        for item in data['objects']:
            writer = csv.DictWriter(raw_data, item.keys(), extrasaction='ignore')
            writer.writerow(item)
        return raw_data

    def from_csv(self, content):
        raw_data = StringIO.StringIO(content)
        data = []
        for item in csv.DictReader(raw_data):
            data.append(item)
        return data