import copy
import datetime

import pytest
from django.core import management
from django.test import TestCase as DjangoTestCase
from lxml.builder import E

import iati_codelists.models as codelist_models
from geodata.models import Country
from iati.factory import iati_factory
from iati.parser.parse_manager import ParseManager
from iati_organisation.parser.organisation_2_03 import Parse as OrgParse_203
from iati_synchroniser.factory import synchroniser_factory


class OrganisationsOrganisationTestCase(DjangoTestCase):
    def setUp(self):
        # 'Main' XML file for instantiating parser:
        xml_file_attrs = {
            "generated-datetime": datetime.datetime.now().isoformat(),
            "version": '2.03',
        }
        self.iati_203_XML_file = E("iati-organisations", **xml_file_attrs)

        dummy_source = synchroniser_factory.DatasetFactory(filetype=2).create()

        self.organisation_parser_203 = ParseManager(
            dataset=dummy_source,
            root=self.iati_203_XML_file,
        ).get_parser()

        

    def test_iati_organisations__iati_organisation(self):
        organisation_attribute = {"last-updated-datetime": "2014-09-10",
                                  "xml:lang": "en",
                                  "default-currency": "EUR"}
        organisation_XML_element = E("iati-organisation",
                                     E("organisation-identifier","AA-AAA_123"),
                                     **organisation_attribute)


