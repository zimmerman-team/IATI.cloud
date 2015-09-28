from django.test import TestCase
import unittest
from mock import MagicMock

from lxml.etree import Element

from iati.models import AidType
from iati.models import AidTypeCategory
from iati.models import Country
from iati_synchroniser.codelist_importer import CodeListImporter
from iati.factory import iati_factory


class CodelistImporterTestCase(TestCase):

    """
        Test code list importer functionality
    """

    def test_add_aid_type_category_item(self):
        """
        Test adding an AidTypeCategory code list item
        """

        code_text = 'A'
        name_text = 'Budget support'
        description_text = 'For contributions under this category...'

        # use factory to create AidTypeCategory, check if set on model
        aidTypeCategory = iati_factory.AidTypeCategoryFactory.create(code=code_text, name=name_text, description=description_text)

        element = Element('AidType-category')
        code = Element('code')
        code.text = code_text

        name = Element('name')
        name.text = name_text

        description = Element('description')
        description.text = description_text

        element.extend([code, name, description])

        importer = CodeListImporter()
        importer.add_code_list_item(element)

        self.assertEqual(1, AidTypeCategory.objects.count(),
            "New AidTypeCategory should be added into database")

        self.assertEqual(aidTypeCategory, AidTypeCategory.objects.all()[0],
            "New AidTypeCategory should match input")

    def test_add_aid_type_item(self):
        """
        Test adding an AidType code list item
        """

        # category should already be in the db
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

    def test_add_missing_items(self):

        importer = CodeListImporter()
        importer.add_missing_items()

        self.assertEqual(2, Country.objects.count())

    def test_add_to_model_if_field_exists(self):

        aid_type_item = iati_factory.AidTypeFactory.create(code='A')

        fake_description = 'added_through_add_to_model_if_field_exists'

        importer = CodeListImporter()

        aid_type_item = importer.add_to_model_if_field_exists(
            AidType,
            aid_type_item,
            'description',
            'added_through_add_to_model_if_field_exists')

        # case; should be added
        self.assertEqual(fake_description, aid_type_item.description)

        aid_type_item2 = importer.add_to_model_if_field_exists(
            AidType,
            aid_type_item,
            'non_existing_field_for_this_model',
            'added_through_add_to_model_if_field_exists')

        # case; should not be added
        with self.assertRaises(AttributeError):
            non_existing_field = aid_type_item.non_existing_field_for_this_model

        # and the function should still return the item
        self.assertEqual(aid_type_item, aid_type_item2)


    @unittest.skip("Not implemented")
    def test_loop_through_codelists(self):
        return False

    @unittest.skip("Not implemented")
    def test_get_codelist_data(self):
        return False

    def test_synchronise_with_codelists(self):

        importer = CodeListImporter()
        importer.get_codelist_data = MagicMock()
        importer.loop_through_codelists = MagicMock()

        importer.synchronise_with_codelists()

        self.assertEqual(9, importer.get_codelist_data.call_count)
        self.assertEqual(len(importer.iati_versions), importer.loop_through_codelists.call_count)
        importer.get_codelist_data.assert_called_with(name='DocumentCategory-category')
        importer.loop_through_codelists.assert_called_with('1.04')


