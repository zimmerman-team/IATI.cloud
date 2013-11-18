__author__ = 'vincentvantwestende'
from IATI.models import *
import urllib2
from lxml import etree
from geodata.models import country, region

class CodeListImporter():

    def synchronise_with_codelists(self):


        #get the file
        downloaded_xml = urllib2.Request("http://datadev.aidinfolabs.org/data/codelist.xml")
        file_opener = urllib2.build_opener()
        xml_file = file_opener.open(downloaded_xml)



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


            try:
                if type == "ActivityDateType" :
                    db_row = activity_date_type(code=code, name=name)

                elif type == "ActivityStatus" :
                    db_row = activity_status(code=code, name=name, language=language_name)

                elif type == "AidType" :
                    db_row2 = aid_type_category(code=category, name=category_name, description=category_description)
                    db_row2.save()
                    db_row = aid_type(code=code, name=name, description=description, category=db_row2)

                elif type == "Country" :
                    name = name.lower().capitalize()
                    db_row = country(code=code, name=name, language=language_name)

                elif type == "BudgetType" :
                    db_row = budget_type(code=code, name=name, language=language_name)

                elif type == "CollaborationType" :
                    db_row = collaboration_type(code=code, name=name, description=description, language=language_name)

                elif type == "ConditionType" :
                    db_row = condition_type(code=code, name=name, language=language_name)

                elif type == "Currency" :
                    db_row = currency(code=code, name=name, language=language_name)

                elif type == "DescriptionType" :
                    db_row = description_type(code=code, name=name, description=description)

                elif type == "DisbursementChannel" :
                    db_row = disbursement_channel(code=code, name=name)

                elif type == "DocumentCategory" :
                    db_row = document_category(code=code, name=name, description=description, category=category, category_name=category_name)

                elif type == "FileFormat" :
                    db_row = file_format(code=code, name=name)

                elif type == "FinanceType" :
                    db_row2 = finance_type_category(code=category, name=category_name ,description=category_description)
                    db_row2.save()
                    db_row = finance_type(code=code, name=name, category=db_row2)

                elif type == "FlowType" :
                    db_row = flow_type(code=code, name=name, description=description)

                elif type == "GazetteerAgency" :
                    db_row = gazetteer_agency(code=code, name=name)


                elif type == "GeographicalPrecision" :
                    db_row = geographical_precision(code=code, name=name, description=description)


                elif type == "IndicatorMeasure" :
                    db_row = indicator_measure(code=code, name=name)

                elif type == "Language" :
                    db_row = language(code=code, name=name)


                elif type == "LocationType" :
                    db_row = location_type(code=code, name=name)


                elif type == "OrganisationalIdentifier" :
                    db_row = organisation_identifier(code=code,abbreviation=abbreviation, name=name)


                elif type == "OrganisationRole" :
                    db_row = organisation_role(code=code, name=name, description=description)

                elif type == "OrganisationType" :
                    db_row = organisation_type(code=code, name=name)


                elif type == "PolicyMarker" :
                    db_row = policy_marker(code=code, name=name)


                elif type == "PolicySignificance" :
                    db_row = policy_significance(code=code, name=name, description=description)

                elif type == "PublisherType" :
                    db_row = publisher_type(code=code, name=name)

                elif type == "Region" :
                    db_row = region(code=code, name=name, source="DAC")

                elif type == "RelatedActivityType" :
                    db_row = related_activity_type(code=code, name=name, description=description)

                elif type == "ResultType" :
                    db_row = result_type(code=code, name=name)

                elif type == "Sector" :
                    db_row = sector(code=code, name=name, description=description)

                elif type == "SectorCategory" :
                    name = name.lower().capitalize()
                    db_row = sector_category(code=code, name=name, description=description)

                elif type == "TiedStatus" :
                    db_row = tied_status(code=code, name=name, description=description)

                elif type == "TransactionType" :
                    db_row = transaction_type(code=code, name=name, description=description)

                elif type == "ValueType" :
                    db_row = value_type(code=code, name=name, description=description)

                elif type == "VerificationStatus" :
                    db_row = verification_status(code=code, name=name)

                elif type == "Vocabulary" :
                    db_row = vocabulary(code=code, name=name)


                if (db_row is not None):
                    db_row.save()

            except Exception as e:
                print "error in codelists"
                print '%s (%s)' % (e.message, type(e))
                print e.messages
                raise

        def add_missing_items():
            if not country.objects.filter(code="XK").exists():
                kosovo = country(code="XK", name="Kosovo", language="en")
                kosovo.save()



        def get_codelist_data(elem):
            name = (elem.xpath( 'name/text()' ))
            cur_downloaded_xml = "http://datadev.aidinfolabs.org/data/codelist/" + name[0] + ".xml"
            cur_file_opener = urllib2.build_opener()
            cur_xml_file = cur_file_opener.open(cur_downloaded_xml)

            if (name[0] == "OrganisationIdentifier"):
                name[0] = "OrganisationalIdentifier"

            context = etree.iterparse( cur_xml_file, tag=name[0] )
            fast_iter(context, add_code_list_item)

            add_missing_items()


        #iterate through code lists
        context = etree.iterparse( xml_file, tag='codelist' )
        fast_iter(context, get_codelist_data)


