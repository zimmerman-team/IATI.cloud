from django.test import TestCase as DjangoTestCase
from django.utils.encoding import smart_text


class UtilTestCase(DjangoTestCase):

    def test_normalise_unicode_string(self):
        self.assertEquals(smart_text('\xa0'), '\xa0')
        self.assertEquals(smart_text(u'a'), u'a')
