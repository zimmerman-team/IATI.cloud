from django.test import TestCase as DjangoTestCase
from common.util import normalise_unicode_string


class UtilTestCase(DjangoTestCase):

    def test_normalise_unicode_string(self):
        self.assertEquals(normalise_unicode_string('\xa0'), '\xa0')
        self.assertEquals(normalise_unicode_string(u'\xa0'), u' ')
        self.assertEquals(normalise_unicode_string(u'a'), u'a')
