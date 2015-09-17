"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

from django.test import TestCase as DjangoTestCase # Runs each test in a transaction and flushes database
from unittest import TestCase 

def build_xml():
    """
        Construct a base activity file to work with in the tests
    """
    pass

class XMLSetup(TestCase):
    def setUp(self):
        self.root = build_xml()

        root = etree.Element("root")
        

    def tearDown(self):
        pass

class Organisation(DjangoTestCase):
    pass

class ActivityTestCase(DjangoTestCase):

