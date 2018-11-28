import urllib.request
from unittest import TestCase

import xlrd


class TestFilter(TestCase):

    # basically downloads some data in xls format
    # with export fields applied and checks if the fields exist
    def test_xls_export_fields(self):
        # This is basically how the export fields look,
        # that are used in the
        # below url
        export_fields = {
            "title.narratives.0.text": "Project title",
            "title.id": "Project id",
            "iati_identifier": "IATI Identifier"
        }

        link = 'http://localhost:8000/api/activities/?export_fields=' \
               '%7B%22title.narratives.0.text%22%3A%22Project+' \
               'title%22%2C%22title.id%22%3A%22Project+id%22%2C%22iati_' \
               'identifier%22%3A%22IATI+Identifier%22%7D&format=xls'
        file_name, headers = urllib.request.urlretrieve(link)

        workbook = xlrd.open_workbook(file_name)

        xl_sheet = workbook.sheet_by_index(0)
        row = xl_sheet.row(0)  # 1st row

        for idx, cell_obj in enumerate(row):
            column_name = cell_obj.value
            column_name_exists = column_name in export_fields.values()
            self.assertTrue(column_name_exists)
            export_fields = {key: val for key, val in export_fields.items()
                             if val != column_name}
