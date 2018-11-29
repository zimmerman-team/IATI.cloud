import base64
import datetime
import urllib.request
from django.test import TestCase, RequestFactory
from rest_framework.reverse import reverse

from iati.models import Activity
from iati.parser.parse_manager import ParseManager
from lxml.builder import E

from iati.factory.iati_factory import (ResultFactory, ActivityFactory)
from iati_synchroniser.factory import synchroniser_factory

from django.test import Client

import xlrd


class TestFilter(TestCase):

    def setUp(self):
        ActivityFactory()

    # basically downloads some data in xls format
    # with export fields applied and checks if the fields exist
    def test_xls_export_fields(self):
        link = reverse('activities:activity-list') + '1/?export_fields=' \
                                                     '%7B%22title.narratives.0.text%22%3A%22Project+' \
                                                     'title%22%2C%22title.id%22%3A%22Project+id%22%2C%22iati_' \
                                                     'identifier%22%3A%22IATI+Identifier%22%7D&format=xls'
        c = Client()
        response = c.get(link)

        # This is basically how the export fields look,
        # that are used in the
        # below url
        export_fields = {
            "title.narratives.0.text": "Project title",
            "title.id": "Project id",
            "iati_identifier": "IATI Identifier"
        }

        workbook = xlrd.open_workbook(file_contents=response.content)

        xl_sheet = workbook.sheet_by_index(0)
        row = xl_sheet.row(0)  # 1st row

        for idx, cell_obj in enumerate(row):
            column_name = cell_obj.value
            column_name_exists = column_name in export_fields.values()
            self.assertTrue(column_name_exists)
            export_fields = {key: val for key, val in export_fields.items()
                             if val != column_name}
