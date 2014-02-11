__author__ = 'vincentvantwestende'
from iati.models import *
import urllib2
from lxml import etree
from geodata.models import Country, Region
from iati.models import RegionVocabulary
import logging
logger = logging.getLogger(__name__)

class CodeListImporter():

    def synchronise_with_codelists(self):

        def fast_iter(context, func):
            for event, elem in context:
                func(elem)
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
            del context

        def return_first_exist(xpath_find):

            if not xpath_find:
                 xpath_find = None
            else:
                # xpath_find = xpath_find[0].encode('utf-8')
                try:
                    xpath_find = unicode(xpath_find[0], errors='ignore')
                except:
                    xpath_find = xpath_find[0]

                xpath_find = xpath_find.encode('utf-8')
            return xpath_find


        def add_code_list_item(elem):
            type = elem.tag

            db_row = None

            code = elem.xpath('code/text()')
            name = elem.xpath('name/text()')
            description = elem.xpath('description/text()')
            language_name = elem.xpath('language/text()')
            category = elem.xpath('category/text()')
            category_name = elem.xpath('category-name/text()')
            category_description = elem.xpath('category-description/text()')
            abbreviation = elem.xpath('abbreviation/text()')
            sector = elem.xpath('sector/text()')

            if not code:
                code = ""
            else:
                code = return_first_exist(code)
            if not name:
                name = ""
            else:
                name = return_first_exist(name)
            if not description:
                description = ""
            else:
                description = return_first_exist(description)
            if not language_name:
                language_name = ""
            else:
                language_name = return_first_exist(language_name)
            if not category:
                category = ""
            else:
                category = return_first_exist(category)
            if not category_name:
                category_name = ""
            else:
                category_name = return_first_exist(category_name)
            if not category_description:
                category_description = ""
            else:
                category_description = return_first_exist(category_description)
            if not abbreviation:
                abbreviation = ""
            else:
                abbreviation = return_first_exist(abbreviation)
            if not sector:
                sector = ""
            else:
                sector = return_first_exist(sector)


            try:
                if type == "ActivityDateType":
                    db_row = ActivityDateType(code=code, name=name)

                elif type == "ActivityStatus":
                    db_row = ActivityStatus(code=code, name=name, language=language_name)

                elif type == "Country":
                    name = name.lower().capitalize()
                    db_row = Country(code=code, name=name, language=language_name)

                elif type == "BudgetType":
                    db_row = BudgetType(code=code, name=name, language=language_name)

                elif type == "CollaborationType":
                    db_row = CollaborationType(code=code, name=name, description=description, language=language_name)

                elif type == "ConditionType":
                    db_row = ConditionType(code=code, name=name, language=language_name)

                elif type == "Currency":
                    db_row = Currency(code=code, name=name, language=language_name)

                elif type == "DescriptionType":
                    db_row = DescriptionType(code=code, name=name, description=description)

                elif type == "DisbursementChannel":
                    db_row = DisbursementChannel(code=code, name=name)

                elif type == "DocumentCategory":
                    db_row = DocumentCategory(code=code, name=name, description=description, category=category, category_name=category_name)

                elif type == "FileFormat":
                    db_row = FileFormat(code=code, name=name)

                elif type == "FlowType":
                    db_row = FlowType(code=code, name=name, description=description)

                elif type == "GazetteerAgency":
                    db_row = GazetteerAgency(code=code, name=name)

                elif type == "GeographicalPrecision":
                    db_row = GeographicalPrecision(code=code, name=name, description=description)

                elif type == "IndicatorMeasure":
                    db_row = ResultIndicatorMeasure(code=code, name=name)

                elif type == "Language":
                    db_row = Language(code=code, name=name)

                elif type == "LocationType":
                    db_row = LocationType(code=code, name=name)

                elif type == "OrganisationIdentifier":
                    db_row = OrganisationIdentifier(code=code,abbreviation=abbreviation, name=name)

                elif type == "OrganisationRole":
                    db_row = OrganisationRole(code=code, name=name, description=description)

                elif type == "OrganisationType":
                    db_row = OrganisationType(code=code, name=name)

                elif type == "PolicyMarker":
                    db_row = PolicyMarker(code=code, name=name)

                elif type == "PolicySignificance":
                    db_row = PolicySignificance(code=code, name=name, description=description)

                elif type == "PublisherType":
                    db_row = PublisherType(code=code, name=name)

                elif type == "RelatedActivityType":
                    db_row = RelatedActivityType(code=code, name=name, description=description)

                elif type == "ResultType":
                    db_row = ResultType(code=code, name=name)

                elif type == "SectorCategory":
                    name = name.lower().capitalize()
                    db_row = SectorCategory(code=code, name=name, description=description)

                elif type == "TiedStatus":
                    db_row = TiedStatus(code=code, name=name, description=description)

                elif type == "TransactionType":
                    db_row = TransactionType(code=code, name=name, description=description)

                elif type == "ValueType":
                    db_row = ValueType(code=code, name=name, description=description)

                elif type == "VerificationStatus":
                    db_row = VerificationStatus(code=code, name=name)

                elif type == "Vocabulary":
                    db_row = Vocabulary(code=code, name=name)

                elif type == "ActivityScope":
                    db_row = ActivityScope(code=code, name=name)

                elif type == "AidTypeFlag":
                    db_row = AidTypeFlag(code=code, name=name)

                elif type == "BudgetIdentifier":
                    db_row = BudgetIdentifier(code=code, name=name, category=category, sector=sector)

                elif type == "BudgetIdentifierVocabulary":
                    db_row = BudgetIdentifierVocabulary(code=code, name=name)

                elif type == "ContactType":
                    db_row = ContactType(code=code, name=name)

                elif type == "LoanRepaymentPeriod":
                    db_row = LoanRepaymentPeriod(code=code, name=name)

                elif type == "LoanRepaymentType":
                    db_row = LoanRepaymentType(code=code, name=name)

                elif type == "RegionVocabulary":
                    db_row = RegionVocabulary(code=code, name=name)

                elif type == "FinanceType":
                    db_row2 = FinanceTypeCategory(code=category, name=category_name ,description=category_description)
                    db_row2.save()
                    db_row = FinanceType(code=code, name=name, category=db_row2)

                elif type == "Region":
                    region_voc = RegionVocabulary.objects.get(code=1)
                    db_row = Region(code=code, name=name, region_vocabulary=region_voc)

                elif type == "AidType":
                        db_row2 = AidTypeCategory(code=category, name=category_name, description=category_description)
                        db_row2.save()
                        db_row = AidType(code=code, name=name, description=description, category=db_row2)

                elif type == "Sector":
                    sector_cat = SectorCategory.objects.get(code=category)
                    db_row = Sector(code=code, name=name, description=description, category=sector_cat)


                if (db_row is not None):
                    db_row.save()

            except Exception as e:

                logger.info("error in codelists")
                logger.info('%s (%s)' % (e.message, type(e)))
                logger.info(e.messages)

        def add_missing_items():
            if not Country.objects.filter(code="XK").exists():
                kosovo = Country(code="XK", name="Kosovo", language="en")
                kosovo.save()


        def get_codelist_data(elem=None, name=None):
            if not name:
                name = (elem.xpath('name/text()'))[0]
            cur_downloaded_xml = "http://data.aidinfolabs.org/data/codelist/" + name + ".xml"
            cur_file_opener = urllib2.build_opener()
            cur_xml_file = cur_file_opener.open(cur_downloaded_xml)

            context2 = etree.iterparse(cur_xml_file, tag=name)
            fast_iter(context2, add_code_list_item)

        #Do sector categories first
        get_codelist_data(name="SectorCategory")
        get_codelist_data(name="RegionVocabulary")

        #get the file
        downloaded_xml = urllib2.Request("http://data.aidinfolabs.org/data/codelist.xml")
        file_opener = urllib2.build_opener()
        xml_file = file_opener.open(downloaded_xml)
        context = etree.iterparse(xml_file, tag='codelist')
        fast_iter(context, get_codelist_data)
        add_missing_items()


