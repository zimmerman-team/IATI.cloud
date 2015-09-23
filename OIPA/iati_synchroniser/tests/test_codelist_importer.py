from django.test import TestCase

from lxml.etree import Element

from iati.models import AidType
from iati_synchroniser.codelist_importer import CodeListImporter
from iati.factory import iati_factory


class CodelistImporterTestCase(TestCase):
    """
    Test CodelistImporter functionality
    """
    def test_aid_type_codelist(self):
        """
        Test if activity source data parsed
        """

        # use factory to create AidTypeCategory, check if set on model
        aidTypeCategory = iati_factory.AidTypeCategoryFactory.create(code='A')

        element = Element('aidType')
        code = Element('code')
        code.text = 'A01'

        name = Element('name')
        name.text = 'General budget support'

        language = Element('language')
        language.text = 'en'

        category = Element('category')
        category.text = 'A'

        description = Element('description')
        description.text = 'test description'

        element.extend([code, name, language, category, description])

        importer = CodeListImporter()
        importer.add_code_list_item(element)

        self.assertEqual(1, AidType.objects.count(),
            "New AidType should be added into database")

        self.assertEqual(aidTypeCategory, AidType.objects.all()[0].category,
            "New AidType should be added into database")
