import datetime
import logging
import urllib

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError
from django.utils.encoding import smart_text
from lxml import etree

from geodata.models import Country, Region
from iati_codelists.models import (
    FileFormat, FinanceTypeCategory, OrganisationIdentifier,
    OrganisationRegistrationAgency, Sector
)
from iati_synchroniser.dac_sector_importer import DacSectorImporter
from iati_synchroniser.models import Codelist
from iati_synchroniser.sdg_sector_importer import SdgSectorImporter
from iati_synchroniser.unesco_sector_importer import UnescoSectorImporter
from iati_vocabulary.models import RegionVocabulary, SectorVocabulary

logger = logging.getLogger(__name__)


class CodeListImporter():
    # TODO: there's lots of same code here (Codelist items are (probably) added
    # (files are downloaded) twice). Code needds to be refactored to the DRY
    # principles.

    def __init__(self):
        self.looping_through_version = "2.03"
        self.iati_versions = ["2.03", ]

    def synchronise_with_codelists(self):
        """These are the Codelists to grab from IATI xml file which lists all
        available codelists.

           - The model name has to match 'name' argument
           - If it doesn't, add an 'if' block in 'add_code_list_item()' method
             in this class
        """
        self.CODELIST_ITEMS_TO_PARSE = [
            # Do categories first
            "SectorCategory",
            "SectorVocabulary",
            "RegionVocabulary",
            "PolicyMarkerVocabulary",
            "IndicatorVocabulary",
            "BudgetIdentifierSector-category",
            "BudgetIdentifierSector",
            "LocationType-category",
            "FinanceType-category",
            "FinanceType",
            "AidType-category",
            # TODO: update test:
            "AidTypeVocabulary",
            "DocumentCategory-category",
            "TagVocabulary",
        ]

        for codelist_name in self.CODELIST_ITEMS_TO_PARSE:
            # This adds Codelist ITEMS (not Codelist objects):
            # FIXME: although, they are (probably) already added here TWICE
            # TODO: refactor this whole code so double functionality according
            # to DRY principles:
            self.get_codelist_data(name=codelist_name)

        # This loops through IATI versions and creates Codelist ITEMS:
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
        '''Adds ALL available codelist items from the file IF element's name
        matches model name in our database (RegionVocabulary, Country, etc.)
        '''

        tag = elem.tag
        item = None
        code = smart_text(self.return_first(elem.xpath('code/text()')))
        name = smart_text(self.return_first(elem.xpath('name/text()')))
        description = smart_text(self.return_first(
            elem.xpath('description/text()'))) or ''
        language_name = smart_text(
            self.return_first(elem.xpath('language/text()')))
        category = smart_text(self.return_first(elem.xpath('category/text()')))
        url = smart_text(self.return_first(elem.xpath('url/text()'))) or ' '
        model_name = tag

        # If Codelist name in IATI's file is different from our model name (or
        # if other modifications are needed), such conditions should be
        # overriden here:

        if tag == "Country":
            name = name.lower().title()
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

        elif tag == "FinanceType":
            model_name = 'FinanceType'

        elif tag == "Region":
            region_voc = RegionVocabulary.objects.get(code=1)
            item = Region(region_vocabulary=region_voc)

        elif tag == "Sector":
            sector_vocabulary = SectorVocabulary.objects.get(code=1)
            item = Sector(vocabulary=sector_vocabulary)

        elif tag == "AidType-category":
            model_name = 'AidTypeCategory'

        elif tag == "CRSAddOtherFlags":
            model_name = 'OtherFlags'

        elif tag == "CRSChannelCode":
            name = name[:255]

        elif tag == "Version":
            if url is None:
                url = 'http://iatistandard.org/' + \
                    self.looping_through_version.replace('.', '')

        if name is None or name == '':
            logger.log(0, 'name is null in ' + tag)
            name = code

        model = None
        try:
            # to do; change app_label to iati_codelist after codelist app
            # change
            model = apps.get_model(
                app_label='iati_codelists', model_name=model_name)
        except LookupError:
            pass

        try:
            # to do; change app_label to iati_codelist after codelist app
            # change
            model = apps.get_model(
                app_label='iati_vocabulary', model_name=model_name)
        except LookupError:
            pass

        if not model:
            try:
                model = apps.get_model(
                    app_label='geodata', model_name=model_name)
            except LookupError:
                print(''.join(['Model not found: ', model_name]))
                return False

        if not item:
            item = model()

        item.code = code
        item.name = name

        if len(item.name) > 200:
            item.name = item.name[0:200]
            print("name of code: {} , name: {} shortened to 200".format(
                item.code, item.name))

        item.codelist_iati_version = self.looping_through_version

        item = self.add_to_model_if_field_exists(
            model, item, 'description', description)
        item = self.add_to_model_if_field_exists(model, item, 'url', url)

        if category and model_name == 'FinanceType':
            ft_cat = FinanceTypeCategory.objects.filter(
                # currently 'code' field is used as a PK for this model:
                code=category,
            ).first()

            if ft_cat:
                item.category = ft_cat

        # FIXME: refactor this general abstract approach with models!:
        if category:
            item = self.add_to_model_if_field_exists(
                model, item, 'category_id', category)

        if item is not None and not model.objects.filter(
            pk=item.code
        ).exists():
            try:
                item.save()
            except IntegrityError as err:
                print("Error: {}".format(err))
                pass

    def add_to_model_if_field_exists(
            self, model, item, field_name, field_content):
        try:
            model._meta.get_field(field_name)

            # Save all strings as decoded strings and not as bytestrings:
            if type(field_content) == bytes and not field_content.isdigit():
                field_content = smart_text(field_content)

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
        Country.objects.get_or_create(
            code="AC",
            defaults={
                'name': 'Ascension Island',
                'language': 'en'})
        Country.objects.get_or_create(
            code="TA",
            defaults={
                'name': 'Tristan da Cunha',
                'language': 'en'})

    def get_codelist_data(self, elem=None, name=None):
        '''If 'name' parameter is not passed to this funtion, it first creates
           Codelist objects.
           Otherwise, actual codelist items (RegionVocabulary, SectorCategory)
           are also created
        '''

        if not name:
            name = smart_text(self.return_first(elem.xpath('name/text()')))
            description = smart_text(
                self.return_first(elem.xpath('description/text()'))
            )
            count = smart_text(self.return_first(elem.xpath('count/text()')))
            fields = smart_text(self.return_first(elem.xpath('fields/text()')))
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

        codelist_file_url = ("http://reference.iatistandard.org/"
                             + self.looping_through_version.replace('.', '') +
                             "/codelists/downloads/clv1/"
                             "codelist/" + smart_text(name) + ".xml")

        cur_file_opener = urllib.request.build_opener()

        try:
            cur_xml_file = cur_file_opener.open(codelist_file_url)

            context2 = etree.iterparse(cur_xml_file, tag=name)
            self.fast_iter(context2, self.add_code_list_item)

        # FIXME: log this error!:
        # TODO: present 404s to frontend
        except urllib.error.HTTPError:
            raise Exception(
                'Codelist URL not found: {0}'.format(codelist_file_url)
            )

    def loop_through_codelists(self, version):
        downloaded_xml = urllib.request.Request(
            "http://reference.iatistandard.org/"
            + version.replace('.', '') +
            "/codelists/downloads/clv1/codelist.xml")

        file_opener = urllib.request.build_opener()
        xml_file = file_opener.open(downloaded_xml)
        context = etree.iterparse(xml_file, tag='codelist')
        # This updates / creates new Codelist objects (name argument is not
        # passed to 'get_codelist_data') AND adds Codelist items:
        self.fast_iter(context, self.get_codelist_data)
        self.add_missing_items()

        # XXX: where are these used?
        # Some of them (from the JSON file) dublicate with official Sectors:
        # reference.iatistandard.org/203/codelists/downloads/clv1/codelist/Sector.xml  # NOQA: E501
        dsi = DacSectorImporter()
        dsi.update()

        # These look like Unesco-specific Sectors, but despite the fact
        # that they are not in IATI (we can not parse them), they are
        # (will be) used globally, so we have to keep them in OIPA:
        ssi = SdgSectorImporter()
        ssi.update()

        # Unesco-specific sectors (they shouldn't be in OIPA):
        usi = UnescoSectorImporter()
        usi.update()
