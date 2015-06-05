import urllib2
import logging
import datetime
from lxml import etree

from django.db import IntegrityError

from iati.models import *
from geodata.models import Country, Region
from iati.models import RegionVocabulary
from iati_synchroniser.models import Codelist
import pprint

logger = logging.getLogger(__name__)


class CodeListImporter():

    looping_through_version = ""
    iati_versions = ["1.04", "1.05", "2.01"]

    def synchronise_with_codelists(self):

        def fast_iter(context, func):
            for event, elem in context:
                func(elem)
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
            del context

        def return_first(xpath_find):
            if xpath_find:
                return xpath_find[0].encode('utf-8')
            else:
                return None

        def add_code_list_item(elem):

            tag = elem.tag
            db_row = None

            code = return_first(elem.xpath('code/text()'))
            name = return_first(elem.xpath('name/text()'))
            description = return_first(elem.xpath('description/text()')) or ''
            language_name = return_first(elem.xpath('language/text()'))
            category = return_first(elem.xpath('category/text()'))
            url = return_first(elem.xpath('url/text()'))

            if tag == "ActivityDateType":
                db_row = ActivityDateType(
                    description=description)

            elif tag == "ActivityStatus":
                db_row = ActivityStatus(
                    description=description)

            elif tag == "Country":
                name = name.lower().capitalize()
                db_row = Country(
                    language=language_name,
                    data_source="IATI")

            elif tag == "BudgetType":
                db_row = BudgetType(
                    description=description)

            elif tag == "CollaborationType":
                db_row = CollaborationType(
                    description=description)

            elif tag == "ConditionType":
                db_row = ConditionType(
                    description=description)

            elif tag == "Currency":
                db_row = Currency(
                    description=description)

            elif tag == "DescriptionType":
                db_row = DescriptionType(
                    description=description)

            elif tag == "DisbursementChannel":
                db_row = DisbursementChannel(
                    description=description)

            elif tag == "DocumentCategory-category":
                db_row = DocumentCategoryCategory(
                    description=description)

            elif tag == "DocumentCategory":
                dcc = DocumentCategoryCategory.objects.get(code=category)

                db_row = DocumentCategory(
                    description=description,
                    category=dcc)

            elif tag == "GeographicLocationClass":
                db_row = GeographicLocationClass(
                    description=description)

            elif tag == "FileFormat":
                db_row = FileFormat(
                    description=description,
                    category=category)

            elif tag == "FlowType":
                db_row = FlowType(
                    description=description)

            elif tag == "GazetteerAgency":
                db_row = GazetteerAgency(
                    description=description)

            elif tag == "GeographicalPrecision":
                db_row = GeographicalPrecision(
                    description=description)

            elif tag == "IndicatorMeasure":
                db_row = IndicatorMeasure(
                    description=description)

            elif tag == "Language":
                db_row = Language(
                    description=description)

            elif tag == "LocationType-category":
                db_row = LocationTypeCategory(
                    description=description)

            elif tag == "LocationType":
                ltc = LocationTypeCategory.objects.get(
                    code=category)
                db_row = LocationType(
                    description=description,
                    category=ltc)

            elif tag == "OrganisationIdentifier":
                db_row = OrganisationIdentifier(
                    abbreviation=None)

            elif tag == "IATIOrganisationIdentifier":
                db_row = OrganisationIdentifier(
                    abbreviation=None)

            elif tag == "OrganisationRole":
                db_row = OrganisationRole(
                    description=description)

            elif tag == "OrganisationType":
                db_row = OrganisationType(
                    description=description)

            elif tag == "PolicyMarker":
                db_row = PolicyMarker(
                    description=description)

            elif tag == "PolicySignificance":
                db_row = PolicySignificance(
                    description=description)

            elif tag == "PublisherType":
                db_row = PublisherType(
                    description=description)

            elif tag == "RelatedActivityType":
                db_row = RelatedActivityType(
                    description=description)

            elif tag == "ResultType":
                db_row = ResultType(
                    description=description)

            elif tag == "SectorCategory":
                name = name.lower().capitalize()
                db_row = SectorCategory(
                    description=description)

            elif tag == "TiedStatus":
                db_row = TiedStatus(
                    description=description)

            elif tag == "TransactionType":
                db_row = TransactionType(
                    description=description)

            elif tag == "ValueType":
                db_row = ValueType(
                    description=description)

            elif tag == "VerificationStatus":
                db_row = VerificationStatus(
                    description=description)

            elif tag == "Vocabulary":
                db_row = Vocabulary(
                    description=description)

            elif tag == "ActivityScope":
                db_row = ActivityScope(
                    description=description)

            elif tag == "AidTypeFlag":
                db_row = AidTypeFlag(
                    description=description)

            elif tag == "BudgetIdentifier":
                bis = BudgetIdentifierSector.objects.get(
                    code=category)
                db_row = BudgetIdentifier(
                    description=description,
                    category=bis)

            elif tag == "BudgetIdentifierSector-category":
                db_row = BudgetIdentifierSectorCategory(
                    description=description)

            elif tag == "BudgetIdentifierSector":
                bisc = BudgetIdentifierSectorCategory.objects.get(
                    code=category)
                db_row = BudgetIdentifierSector(
                    description=description,
                    category=bisc)

            elif tag == "BudgetIdentifierVocabulary":
                db_row = BudgetIdentifierVocabulary(
                    description=description)

            elif tag == "ContactType":
                db_row = ContactType(
                    description=description)

            elif tag == "LoanRepaymentPeriod":
                db_row = LoanRepaymentPeriod(
                    description=description)

            elif tag == "LoanRepaymentType":
                db_row = LoanRepaymentType(
                    description=description)

            elif tag == "RegionVocabulary":
                db_row = RegionVocabulary(
                    description=description)

            elif tag == "FinanceType":
                ftc = FinanceTypeCategory.objects.get(code=category)
                db_row = FinanceType(
                    description=description,
                    category=ftc)

            elif tag == "FinanceType-category":
                db_row = FinanceTypeCategory(
                    description=description)

            elif tag == "Region":
                region_voc = RegionVocabulary.objects.get(code=1)
                db_row = Region(
                    region_vocabulary=region_voc)

            elif tag == "AidType-category":
                db_row = AidTypeCategory(
                    description=description)

            elif tag == "AidType":
                atc = AidTypeCategory.objects.get(code=category)
                db_row = AidType(
                    description=description,
                    category=atc)

            elif tag == "Sector":
                sector_cat = SectorCategory.objects.get(code=category)
                db_row = Sector(
                    description=description,
                    category=sector_cat)

            # v1.04 added codelists

            elif tag == "GeographicLocationReach":
                db_row = GeographicLocationReach(
                    description=description)

            elif tag == "OrganisationRegistrationAgency":
                if url == None:
                    url = 'http://iatistandard.org/'+self.looping_through_version.replace('.','')
                db_row = OrganisationRegistrationAgency(
                    description=description,
                    category=category,
                    url=url)

            elif tag == "GeographicExactness":
                if url == None:
                    url = 'http://nourl.org/'
                db_row = GeographicExactness(
                    description=description,
                    category=category,
                    url=url)

            elif tag == "GeographicVocabulary":
                if url == None:
                    url = 'http://nourl.org/'
                db_row = GeographicVocabulary(
                    description=description,
                    url=url)

            elif tag == "PolicyMarkerVocabulary":
                db_row = PolicyMarkerVocabulary(
                    description=description)

            elif tag == "CRSAddOtherFlags":
                db_row = OtherFlags(
                    description=description)

            elif tag == "OtherIdentifierType":
                db_row = OtherIdentifierType(
                    description=description)

            elif tag == "SectorVocabulary":
                print 'in '+tag
                if url == None:
                    url = 'http://iatistandard.org/'+self.looping_through_version.replace('.','')
                db_row = SectorVocabulary(
                    description=description,
                    url=url)

            elif tag == "Version":
                if url == None:
                    url = 'http://iatistandard.org/'+self.looping_through_version.replace('.','')
                db_row = Version(
                    description=description,
                    url=url)

            else:
                print "type not saved: " + tag

            if name == None or name == '':
                logger.log(0,'name is null in '+tag)
                #print 'name is null in '+tag
                name = code

            db_row.code = code
            db_row.name = name

            db_row.codelist_iati_version = self.looping_through_version

            if db_row is not None:
                try:
                    db_row.save()
                except IntegrityError as err:
                    print("Error: {}".format(err))
                    #already saved
                    print tag+" not saved"
                    pprint.pprint(db_row)

                    return None

        def add_missing_items():
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

        def get_codelist_data(elem=None, name=None):

            if not name:
                name = return_first(elem.xpath('name/text()'))
                description = return_first(elem.xpath('description/text()'))
                count = return_first(elem.xpath('count/text()'))
                fields = return_first(elem.xpath('fields/text()'))
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

            else:
                print name

            cur_downloaded_xml = ("http://iatistandard.org/"
                                  + self.looping_through_version.replace('.','') +
                                  "/codelists/downloads/clv1/"
                                  "codelist/" + name + ".xml")
            print cur_downloaded_xml
            cur_file_opener = urllib2.build_opener()
            cur_xml_file = cur_file_opener.open(cur_downloaded_xml)

            context2 = etree.iterparse(cur_xml_file, tag=name)
            fast_iter(context2, add_code_list_item)

        def loop_through_codelists(version):
            downloaded_xml = urllib2.Request(
                "http://iatistandard.org/"
                + version.replace('.','') +
                "/codelists/downloads/clv1/codelist.xml")

            file_opener = urllib2.build_opener()
            xml_file = file_opener.open(downloaded_xml)
            context = etree.iterparse(xml_file, tag='codelist')
            fast_iter(context, get_codelist_data)
            add_missing_items()

        #Do sector categories first
        self.looping_through_version = "2.01"
        get_codelist_data(name="SectorCategory")
        get_codelist_data(name="SectorVocabulary")
        get_codelist_data(name="RegionVocabulary")
        get_codelist_data(name="PolicyMarkerVocabulary")
        get_codelist_data(name="BudgetIdentifierSector-category")
        get_codelist_data(name="LocationType-category")
        get_codelist_data(name="FinanceType-category")
        get_codelist_data(name="AidType-category")
        get_codelist_data(name="DocumentCategory-category")
        self.looping_through_version = ""

        for version in self.iati_versions:
            self.looping_through_version = version
            loop_through_codelists(version)
