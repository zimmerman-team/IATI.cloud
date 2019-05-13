from unittest import skip

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
            "iati_identifier": "IATI Identifier",
            "activity_id": "activity_id",
            'sectors.sector.code': 'sector_code',
            'sectors.percentage': 'sectors_percentage',
            'recipient_countries.country.code': 'country',
            'recipient_regions.region.code': 'region'
        }

        self.xls_export_field_params = 'export_fields=' \
            '%7B%22title.narratives.0.text%22%3A%22Project+' \
            'title%22%2C%22title.id%22%3A%22' \
            'Project+id%22%2C%22iati_' \
            'identifier%22%3A%22IATI+Identifier%22%7D'

        self.format_xls = 'format=xls'
        self.format_csv = 'format=csv'

        self.export_name = 'test'
        self.export_name_param = 'export_name='

        self.activity = ActivityFactory()
        self.activity_detail_link = reverse(
            'activities:activity-detail',
            kwargs={'pk': self.activity.id})

    # basically downloads some data in xls format
    # with export fields applied and checks if the fields exist
    def test_xls_export_fields(self):
        link = self.activity_detail_link + '?'\
                    + self.xls_export_field_params\
                    + '&' + self.format_xls

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

    # basically downloads some data in xls format
    # with an export name specified
    def test_xls_export_specific_name(self):
        link = self.activity_detail_link + '?'\
                    + self.export_name_param\
                    + self.export_name\
                    + '&' + self.format_xls

        c = Client()
        response = c.get(link)

        name_correct = False

        if 'content-disposition' in response._headers:
            if len(response._headers['content-disposition']) > 1:
                # the attachment field retrieved from content disposition
                attachment = response._headers['content-disposition'][1]
                # how the attachment should be in content disposition
                attachment_should = \
                    'attachment; filename={}.xls'.format(self.export_name)
                name_correct = attachment == attachment_should

        self.assertTrue(name_correct)

    # basically downloads some data in csv format
    # with an export name specified
    @skip('NotImplemented')
    def test_csv_export_specific_name(self):
        link = self.activity_detail_link + '?'\
                    + self.export_name_param\
                    + self.export_name\
                    + '&' + self.format_csv

        c = Client()
        response = c.get(link)

        name_correct = False

        if 'content-disposition' in response._headers:
            if len(response._headers['content-disposition']) > 1:
                # the attachment field retrieved from content disposition
                attachment = response._headers['content-disposition'][1]
                # how the attachment should be in content disposition
                attachment_should = \
                    'attachment; filename={}.csv'.format(self.export_name)
                name_correct = attachment == attachment_should

        self.assertTrue(name_correct)

    # basically downloads some data in csv format
    # with an export name specified
    @skip('NotImplemented')
    def test_csv_export_default_name(self):
        link = self.activity_detail_link + '?'\
                    + '&' + self.format_csv

        c = Client()
        response = c.get(link)

        name_correct = False
        # so the filename should be 'activity-list', because
        # the default name is the url name of the view
        # and we already use this url name to compose the link ^
        file_name = 'activity-detail'

        if 'content-disposition' in response._headers:
            if len(response._headers['content-disposition']) > 1:
                # the attachment field retrieved from content disposition
                attachment = response._headers['content-disposition'][1]
                # how the attachment should be in content disposition
                attachment_should = \
                    'attachment; filename={}.csv'.format(file_name)
                name_correct = attachment == attachment_should

        self.assertTrue(name_correct)

    # basically downloads some data in csv format
    # with an export name specified
    def test_xls_export_default_name(self):
        link = self.activity_detail_link + '?'\
                    + '&' + self.format_xls

        c = Client()
        response = c.get(link)

        name_correct = False
        # so the filename should be 'activity-list', because
        # the default name is the url name of the view
        # and we already use this url name to compose the link ^
        file_name = 'activity-detail'

        if 'content-disposition' in response._headers:
            if len(response._headers['content-disposition']) > 1:
                # the attachment field retrieved from content disposition
                attachment = response._headers['content-disposition'][1]
                # how the attachment should be in content disposition
                attachment_should = \
                    'attachment; filename={}.xls'.format(file_name)
                name_correct = attachment == attachment_should

        self.assertTrue(name_correct)

    # so the export middleware should only
    # work with api apps, thus we gonna
    # test it out with the home page
    # and see if the content-dispostion header
    # of the response changes - which means the
    # middleware did activate for it
    # which should NOT be the case
    # the home page should have NO content disposition
    def test_export_middleware_home(self):
        link = reverse('home')

        c = Client()
        response = c.get(link)

        disposition_exists = 'content-disposition' in response._headers

        self.assertFalse(disposition_exists)
