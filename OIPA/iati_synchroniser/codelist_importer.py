import urllib2
import logging
import datetime
from lxml import etree

from django.db import IntegrityError
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist

from iati.models import *
from geodata.models import Country, Region
from iati.models import RegionVocabulary
from iati_synchroniser.models import Codelist

logger = logging.getLogger(__name__)


class CodeListImporter():

    def __init__(self):
        self.looping_through_version = "2.01"
        self.iati_versions = ["2.01"]

    def synchronise_with_codelists(self):
        # Do categories first
        self.get_codelist_data(name="SectorCategory")
        self.get_codelist_data(name="SectorVocabulary")
        self.get_codelist_data(name="RegionVocabulary")
        self.get_codelist_data(name="PolicyMarkerVocabulary")
        self.get_codelist_data(name="BudgetIdentifierSector-category")
        self.get_codelist_data(name="LocationType-category")
        self.get_codelist_data(name="FinanceType-category")
        self.get_codelist_data(name="AidType-category")
        self.get_codelist_data(name="DocumentCategory-category")

        for version in self.iati_versions:
            self.looping_through_version = version
            self.loop_through_codelists(version)

    @staticmethod
    def fast_iter(context, func):
        for event, elem in context:
            func(elem)
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

    @staticmethod
    def return_first(xpath_find):
        if xpath_find:
            return xpath_find[0].encode('utf-8')

    def add_code_list_item(self, elem):

        tag = elem.tag
        item = None
        code = self.return_first(elem.xpath('code/text()'))
        name = self.return_first(elem.xpath('name/text()'))
        description = self.return_first(elem.xpath('description/text()')) or ''
        language_name = self.return_first(elem.xpath('language/text()'))
        category = self.return_first(elem.xpath('category/text()'))
        url = self.return_first(elem.xpath('url/text()')) or ' '
        model_name = tag

        if tag == "ActivityDateType":
            codelist_successor = None
            # if not latest version
            if self.looping_through_version != self.iati_versions[0]:
                if code == 'start-planned':
                    codelist_successor = 1
                if code == 'start-actual':
                    codelist_successor = 2
                if code == 'end-planned':
                    codelist_successor = 3
                if code == 'end-actual':
                    codelist_successor = 4

            item = ActivityDateType(codelist_successor=codelist_successor)

        elif tag == "Country":
            name = name.lower().capitalize()
            item = Country(language=language_name, data_source="IATI")

        elif tag == "DocumentCategory-category":
            model_name = 'DocumentCategoryCategory'

        elif tag == "FileFormat":
            FileFormat(category=category)
            category = None

        elif tag == "OrganisationRegistrationAgency":
            OrganisationRegistrationAgency(category=category)

        elif tag == "LocationType-category":
            model_name = 'LocationTypeCategory'

        elif tag == "OrganisationIdentifier":
            item = OrganisationIdentifier(abbreviation=None)

        elif tag == "IATIOrganisationIdentifier":
            model_name = 'OrganisationIdentifier'
            item = OrganisationIdentifier(abbreviation=None)

        elif tag == "SectorCategory":
            name = name.lower().capitalize()

        elif tag == "BudgetIdentifierSector-category":
            model_name = 'BudgetIdentifierSectorCategory'

        elif tag == "FinanceType-category":
            model_name = 'FinanceTypeCategory'

        elif tag == "Region":
            region_voc = RegionVocabulary.objects.get(code=1)
            item = Region(region_vocabulary=region_voc)

        elif tag == "AidType-category":
            model_name = 'AidTypeCategory'


        elif tag == "CRSAddOtherFlags":
            model_name = 'OtherFlags'

        elif tag == "Version":
            if url is None:
                url = 'http://iatistandard.org/'+self.looping_through_version.replace('.','')

        if name is None or name == '':
            logger.log(0, 'name is null in '+tag)
            name = code

        model = None
        try:
            # to do; change app_label to iati_codelist after codelist app change
            model = apps.get_model(app_label='iati', model_name=model_name)
        except LookupError:
            pass

        if not model:
            try:
                model = apps.get_model(app_label='geodata', model_name=model_name)
            except LookupError:
                print ''.join(['Model not found: ', model_name])

        if not item:
            item = model()

        item.code = code
        item.name = name
        item.codelist_iati_version = self.looping_through_version


        item = self.add_to_model_if_field_exists(model, item, 'description', description)
        item = self.add_to_model_if_field_exists(model, item, 'url', url)
        if category:
            item = self.add_to_model_if_field_exists(model, item, 'category_id', category)

        if item is not None and not model.objects.filter(pk=item.code).exists():
            try:
                item.save()
            except IntegrityError as err:
                print("Error: {}".format(err))
                pass

    def add_to_model_if_field_exists(self, model, item, field_name, field_content):
        try:
            model._meta.get_field(field_name)
            setattr(item, field_name, field_content)
        except FieldDoesNotExist:
            pass
        return item

    def add_missing_items(self):
        Country.objects.get_or_create(
            code="XK",
            defaults={
                'name': 'Kosovo',
                'language': 'en'})
        Country.objects.get_or_create(
            code="YU",
            defaults={
                'name': 'Former Yugoslavia',
                'language': 'en'})

    def get_codelist_data(self, elem=None, name=None):

        if not name:
            name = self.return_first(elem.xpath('name/text()'))
            description = self.return_first(elem.xpath('description/text()'))
            count = self.return_first(elem.xpath('count/text()'))
            fields = self.return_first(elem.xpath('fields/text()'))
            date_updated = datetime.datetime.now()

            if Codelist.objects.filter(name=name).exists():
                current_codelist = Codelist.objects.get(name=name)
                current_codelist.date_updated = date_updated
                current_codelist.description = description
                current_codelist.count = count
                current_codelist.fields = fields
                current_codelist.save()
            else:
                new_codelist = Codelist(
                    name=name,
                    description=description,
                    count=count,
                    fields=fields,
                    date_updated=date_updated)
                new_codelist.save()

        cur_downloaded_xml = ("http://iatistandard.org/"
                              + self.looping_through_version.replace('.','') +
                              "/codelists/downloads/clv1/"
                              "codelist/" + name + ".xml")

        cur_file_opener = urllib2.build_opener()
        cur_xml_file = cur_file_opener.open(cur_downloaded_xml)

        context2 = etree.iterparse(cur_xml_file, tag=name)
        self.fast_iter(context2, self.add_code_list_item)

    def loop_through_codelists(self, version):
        downloaded_xml = urllib2.Request(
            "http://iatistandard.org/"
            + version.replace('.','') +
            "/codelists/downloads/clv2/codelist.xml")

        file_opener = urllib2.build_opener()
        xml_file = file_opener.open(downloaded_xml)
        context = etree.iterparse(xml_file, tag='codelist')
        self.fast_iter(context, self.get_codelist_data)
        self.add_missing_items()

