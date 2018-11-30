import xlrd
from django.test import Client, TestCase
from rest_framework.reverse import reverse

from iati.factory.iati_factory import ActivityFactory


class TestFilter(TestCase):

    def setUp(self):
        # This is basically how the export fields look,
        # that are used in the
        # below url
        self.export_fields = {
            "title.narratives.0.text": "Project title",
            "title.id": "Project id",
            "iati_identifier": "IATI Identifier"
        }

        self.export_field_params = '/?export_fields=' \
            '%7B%22title.narratives.0.text%22%3A%22Project+' \
            'title%22%2C%22title.id%22%3A%22' \
            'Project+id%22%2C%22iati_' \
            'identifier%22%3A%22IATI+Identifier%22%7D&format=xls'

        self.activity = ActivityFactory()

    # basically downloads some data in xls format
    # with export fields applied and checks if the fields exist
    def test_xls_export_fields(self):
        link = reverse('activities:activity-list')
        link = link + str(self.activity.id) + self.export_field_params
        c = Client()
        response = c.get(link)

        workbook = xlrd.open_workbook(file_contents=response.content)

        xl_sheet = workbook.sheet_by_index(0)
        row = xl_sheet.row(0)  # 1st row

        for idx, cell_obj in enumerate(row):
            column_name = cell_obj.value
            column_name_exists = column_name in self.export_fields.values()
            self.assertTrue(column_name_exists)
            self.export_fields = {key: val for key, val in
                                  self.export_fields.items()
                                  if val != column_name}
