from lxml import etree
import urllib2
from iati import models
from iati.management.commands.total_budget_updater import TotalBudgetUpdater
from re import sub
import httplib
from django.db import IntegrityError
from exceptions import TypeError
from django.core.exceptions import ValidationError
import time
from datetime import datetime
from deleter import Deleter
from lxml.etree import XMLSyntaxError
import gc
import logging
import mechanize
import cookielib

logger = logging.getLogger(__name__)

class Parser():

    xml_source_ref = None

    def parse_url(self, url, xml_source_ref):

        try:
            deleter = Deleter()
            deleter.delete_by_source(xml_source_ref)
        except Exception as e:
            print e.args

        try:
            #iterate through iati-activity tree
            iati_file = self.get_the_file(url)
            if iati_file:
                self.xml_source_ref = xml_source_ref
                context = etree.iterparse(iati_file, tag='iati-activity')
                self.fast_iter(context, self.process_element)

                del iati_file
                gc.collect()
        except XMLSyntaxError, e:
            logger.info("XMLSyntaxError" + e.message)
        except Exception as e:
            print e.message



    def get_the_file(self, url, try_number = 0):
        try:

            br = mechanize.Browser()

            # Cookie Jar
            cj = cookielib.LWPCookieJar()
            br.set_cookiejar(cj)

            # Browser options
            br.set_handle_equiv(True)
            br.set_handle_redirect(True)
            br.set_handle_referer(True)
            br.set_handle_robots(False)
            br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
            br.set_debug_http(True)
            br.set_debug_redirects(True)
            br.set_debug_responses(True)

            # User-Agent
            br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

            response = br.open(url, timeout=80)
            return response

            # headers = {'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36'}
            # iati_file_url_object = mechanize.Request(url, headers=headers)
            # file_opener = mechanize.build_opener()
            # iati_file = file_opener.open(iati_file_url_object)
            # return iati_file


        except urllib2.HTTPError, e:
            logger.info('HTTPError (url=' + url + ') = ' + str(e.code))
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            print
            logger.info('URLError (url=' + url + ') = ' + str(e.reason))
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except httplib.HTTPException, e:
            logger.info('HTTPException reading url ' + url)
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except Exception as e:
            logger.info('%s (%s)' % (e.message, type(e)) + " in get_the_file: " + url)



    # loop through the activities, fast_iter starts at the last activity and walks towards the first
    def fast_iter(self, context, func):

        try:
            for event, elem in context:
                try:
                    func(elem)
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e))
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
            del context
        except Exception as e:
            logger.info('%s (%s)' % (e.message, type(e)))



    # remove previously saved data about the activity and store new info
    def process_element(self, elem):

        if self.activity_has_identifier(elem):

            if self.activity_exists(elem):
                self.remove_old_values_for_activity(elem)

            self.add_all_activity_data(elem)


    def add_all_activity_data(self, elem):

        try:

            # add basics
            iati_identifier = self.return_first_exist(elem.xpath('iati-identifier/text()'))
            self.add_organisation(elem)
            activity = self.add_activity(elem)
            self.add_other_identifier(elem, activity)
            self.add_activity_title(elem, activity)
            self.add_activity_description(elem, activity)
            self.add_budget(elem, activity)
            self.add_planned_disbursement(elem, activity)
            self.add_website(elem, activity)
            self.add_contact_info(elem, activity)
            self.add_transaction(elem, activity)
            self.add_result(elem, activity)
            self.add_location(elem, activity)
            self.add_related_activities(elem, activity)
            self.add_conditions(elem, activity)
            self.add_document_link(elem, activity)

            # ManyToMany
            self.add_sectors(elem, activity)
            self.add_participating_organisations(elem, activity)
            self.add_countries(elem, activity)
            self.add_regions(elem, activity)
            self.add_policy_markers(elem, activity)
            self.add_activity_date(elem, activity)

            # Extras
            self.add_total_budget(activity)

        except Exception as e:
                self.exception_handler(e, iati_identifier, "add_all_activity_data")


    # class wide functions
    def return_first_exist(self, xpath_find):

        if not xpath_find:
             xpath_find = None
        else:
            try:
                xpath_find = unicode(xpath_find[0], errors='ignore')
            except:
                xpath_find = xpath_find[0]

            xpath_find = xpath_find.encode('utf-8')
        return xpath_find

    def isInt(self, obj):
        try:
            int(obj)
            return True
        except:
            return False

    def validate_date(self, unvalidated_date):
        valid_date = None
        if unvalidated_date:
            try:
                unvalidated_date = unvalidated_date.split("Z")[0]
                unvalidated_date = sub(r'[\t]', '', unvalidated_date)
                unvalidated_date = unvalidated_date.replace(" ", "")
                unvalidated_date = unvalidated_date.replace("/", "-")
                if len(unvalidated_date) == 4:
                    unvalidated_date = unvalidated_date + "-01-01"
                validated_date = time.strptime(unvalidated_date, '%Y-%m-%d')
                valid_date = datetime.fromtimestamp(time.mktime(validated_date))

            except ValueError:
                logger.info('Invalid date: ' + unvalidated_date)
                valid_date = None
            except Exception as e:
                logger.info(e.message)
        return valid_date


    def activity_exists(self, elem):

        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
        activity_id = activity_id.replace(" ", "")

        if models.Activity.objects.filter(id=activity_id).exists():
            return True
        else:
            return False

    def activity_has_identifier(self, elem):
        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
        if activity_id:
            return True
        return False


    def remove_old_values_for_activity(self, elem):
        deleter = Deleter()
        deleter.remove_old_values_for_activity(elem)


    def delete_all_activities_from_source(self, xml_source_ref):
        deleter = Deleter()
        deleter.delete_by_source(xml_source_ref)


    def exception_handler(self, e, ref, current_def):

        logger.info("error in " + ref + ", def: " + current_def)
        if e.args:
            logger.info(e.args[0])
        if e.args.__len__() > 1:
            logger.info(e.args[1])
        if e.message:
            logger.info(e.message)

    # entity add functions
    def add_organisation(self, elem):
        ref = self.return_first_exist(elem.xpath( 'reporting-org/@ref' ))
        type_ref = self.return_first_exist(elem.xpath( 'reporting-org/@type' ))
        org_type = None
        name = self.return_first_exist(elem.xpath('reporting-org/text()'))
        if ref:
            try:
                if not models.Organisation.objects.filter(code=ref).exists():

                    if not models.OrganisationIdentifier.objects.filter(code=ref).exists():
                        abbreviation = None

                    else:
                        org_identifier = models.OrganisationIdentifier.objects.get(code=ref)
                        abbreviation = org_identifier.abbreviation
                        name = org_identifier.name

                    if type_ref:
                            if self.isInt(type_ref):
                                if models.OrganisationType.objects.filter(code=type_ref).exists():
                                    org_type = models.OrganisationType.objects.get(code=type_ref)
                            elif models.OrganisationType.objects.filter(name=type_ref).exists():
                                org_type = models.OrganisationType.objects.filter(name=type_ref)[0]

                    new_organisation = models.Organisation(code=ref, type=org_type, abbreviation=abbreviation, name=name)
                    new_organisation.save()

                else:
                    existing_organisation = models.Organisation.objects.get(code=ref)
                    if not existing_organisation.name:
                        existing_organisation.name = name
                    if not existing_organisation.abbreviation:
                        if models.OrganisationIdentifier.objects.filter(code=ref).exists():
                            org_identifier = models.OrganisationIdentifier.objects.get(code=ref)
                            existing_organisation.abbreviation = org_identifier.abbreviation
                            existing_organisation.name = org_identifier.name
                    existing_organisation.save()


            except ValueError, e:
                self.exception_handler(e, ref, "add_organisation")
            except TypeError, e:
                self.exception_handler(e, ref, "add_organisation")
            except ValidationError, e:
                self.exception_handler(e, ref, "add_organisation")
            except IntegrityError, e:
                self.exception_handler(e, ref, "add_organisation")
            except Exception as e:
                self.exception_handler(e, ref, "add_organisation")



    def add_activity(self, elem):
        try:
            iati_identifier = self.return_first_exist(elem.xpath('iati-identifier/text()'))
            iati_identifier = iati_identifier.strip(' \t\n\r')
            iati_identifier = iati_identifier.replace(" ", "")
            activity_id = iati_identifier.replace("/", "-")
            activity_id = activity_id.replace(":", "-")



            default_currency_ref = self.return_first_exist(elem.xpath('@default-currency'))
            default_currency = None

            hierarchy = self.return_first_exist(elem.xpath('@hierarchy'))
            last_updated_datetime = self.return_first_exist(elem.xpath('@last-updated-datetime'))
            # if last_updated_datetime:
            #     last_updated_datetime = last_updated_datetime.split('+')[0]
            #     last_updated_datetime = last_updated_datetime.split('-')[0]
            # strp_time = time.strptime(last_updated_datetime_str, '%Y-%m-%d %H:%M:%S')
            # last_updated_datetime = datetime.fromtimestamp(time.mktime(strp_time))

            linked_data_uri = self.return_first_exist(elem.xpath('@linked-data-uri'))
            iati_standard_version = self.return_first_exist(elem.xpath('@version'))

            reporting_organisation_ref = self.return_first_exist(elem.xpath('reporting-org/@ref'))
            reporting_organisation = None

            activity_status_code = self.return_first_exist(elem.xpath('activity-status/@code'))
            activity_status_name = self.return_first_exist(elem.xpath('activity-status/text()'))
            activity_status = None

            collaboration_type_ref = self.return_first_exist(elem.xpath('collaboration-type/@code'))
            collaboration_type = None
            default_flow_type_ref = self.return_first_exist(elem.xpath('default-flow-type/@code'))
            default_flow_type = None
            default_aid_type_ref = self.return_first_exist(elem.xpath('default-aid-type/@code'))
            default_aid_type = None
            default_finance_type_ref = self.return_first_exist(elem.xpath('default-finance-type/@code'))
            default_finance_type = None
            default_tied_status_ref = self.return_first_exist(elem.xpath('default-tied-status/@code'))
            default_tied_status = None
            capital_spend = self.return_first_exist(elem.xpath('capital-spend/@percentage'))
            activity_scope_ref = self.return_first_exist(elem.xpath('activity-scope/@code'))
            activity_scope = None

            #get foreign key objects
            if default_currency_ref:
                if models.Currency.objects.filter(code=default_currency_ref).exists():
                    default_currency = models.Currency.objects.get(code=default_currency_ref)

            #activity status
            if activity_status_code and self.isInt(activity_status_code):
                if models.ActivityStatus.objects.filter(code=activity_status_code).exists():
                    activity_status = models.ActivityStatus.objects.get(code=activity_status_code)

            if reporting_organisation_ref:
                if models.Organisation.objects.filter(code=reporting_organisation_ref).exists():
                    reporting_organisation = models.Organisation.objects.get(code=reporting_organisation_ref)

            if collaboration_type_ref and self.isInt(collaboration_type_ref):
                if models.CollaborationType.objects.filter(code=collaboration_type_ref).exists():
                    collaboration_type = models.CollaborationType.objects.get(code=collaboration_type_ref)

            if default_flow_type_ref and self.isInt(default_flow_type_ref):
                if models.FlowType.objects.filter(code=default_flow_type_ref).exists():
                    default_flow_type = models.FlowType.objects.get(code=default_flow_type_ref)

            if default_aid_type_ref:
                if models.AidType.objects.filter(code=default_aid_type_ref).exists():
                    default_aid_type = models.AidType.objects.get(code=default_aid_type_ref)

            if default_finance_type_ref and self.isInt(default_finance_type_ref):
                if models.FinanceType.objects.filter(code=default_finance_type_ref).exists():
                    default_finance_type = models.FinanceType.objects.get(code=default_finance_type_ref)

            if default_tied_status_ref:

                if not self.isInt(default_tied_status_ref):
                    default_tied_status_ref = default_tied_status_ref.lower()
                    if default_tied_status_ref == "partially tied":
                        default_tied_status_ref = "3"
                    elif default_tied_status_ref == "tied":
                        default_tied_status_ref = "4"
                    elif default_tied_status_ref == "untied":
                        default_tied_status_ref = "5"
                    else:
                        default_tied_status_ref = None

                if models.TiedStatus.objects.filter(code=default_tied_status_ref).exists():
                    default_tied_status = models.TiedStatus.objects.get(code=default_tied_status_ref)

            if not self.isInt(hierarchy):
                hierarchy = None

            if not capital_spend:
                capital_spend = self.return_first_exist(elem.xpath('capital-spend/text()'))

            if not activity_scope_ref:
                activity_scope_ref = self.return_first_exist(elem.xpath('activity-scope/text()'))


            if activity_scope_ref and self.isInt(activity_scope_ref):
                if models.ActivityScope.objects.filter(code=activity_scope_ref).exists():
                    activity_scope = models.ActivityScope.objects.get(code=activity_scope_ref)

            new_activity = models.Activity(id=activity_id, default_currency=default_currency, hierarchy=hierarchy, last_updated_datetime=last_updated_datetime, linked_data_uri=linked_data_uri, reporting_organisation=reporting_organisation, activity_status=activity_status, collaboration_type=collaboration_type, default_flow_type=default_flow_type, default_aid_type=default_aid_type, default_finance_type=default_finance_type, default_tied_status=default_tied_status, xml_source_ref=self.xml_source_ref, iati_identifier=iati_identifier, iati_standard_version=iati_standard_version, capital_spend=capital_spend, scope=activity_scope)
            new_activity.save()
            return new_activity

        except IntegrityError, e:
            self.exception_handler(e, activity_id, "add_activity")
        except ValueError, e:
            self.exception_handler(e, activity_id, "add_activity")
        except ValidationError, e:
            self.exception_handler(e, activity_id, "add_activity")
        except TypeError, e:
            self.exception_handler(e, activity_id, "add_activity")
        except AttributeError as e:
            self.exception_handler(e, activity_id, "add_activity")
        except Exception as e:
            self.exception_handler(e, activity_id, "add_activity")


    #after activity is added

    # add one to many
    def add_other_identifier(self, elem, activity):

        try:
            for t in elem.xpath('other-identifier'):

                try:
                    owner_ref = self.return_first_exist(t.xpath( '@owner-ref' ))
                    owner_name = self.return_first_exist(t.xpath( '@owner-name' ))
                    other_identifier = self.return_first_exist(t.xpath( 'text()' ))

                    new_other_identifier = models.OtherIdentifier(activity=activity, owner_ref=owner_ref, owner_name=owner_name, identifier=other_identifier)
                    new_other_identifier.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_other_identifier")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_other_identifier")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_other_identifier")
        except Exception as e:
                    self.exception_handler(e, activity.id, "add_other_identifier")



    def add_activity_title(self, elem, activity):

        try:
            for t in elem.xpath('title'):
                try:
                    title = self.return_first_exist(t.xpath( 'text()' ))
                    if title:

                        language_ref = self.return_first_exist(t.xpath( '@xml:lang' ))
                        language = None
                        if title.__len__() > 255:
                            title = title[:255]

                        if language_ref:
                            if models.Language.objects.filter(code=language_ref).exists():
                                language = models.Language.objects.get(code=language_ref)


                        new_title = models.Title(activity=activity, title=title, language=language)
                        new_title.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_activity_title")

                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_activity_title")

                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_activity_title")

        except Exception as e:
            self.exception_handler(e, activity.id, "add_activity_title")



    def add_activity_description(self, elem, activity):

        try:
            for t in elem.xpath('description'):
                try:
                    description = self.return_first_exist(t.xpath( 'text()' ))
                    type_ref = self.return_first_exist(t.xpath('@type'))
                    type = None
                    language_ref = self.return_first_exist(t.xpath( '@xml:lang' ))
                    language = None
                    rsr_type_ref = self.return_first_exist(t.xpath( '@akvo:type', namespaces={'akvo': 'http://akvo.org/api/v1/iati-activities'}))
                    rsr_type = None


                    if language_ref:
                        if models.Language.objects.filter(code=language_ref).exists():
                            language = models.Language.objects.get(code=language_ref)

                    if type_ref:
                        try:
                            if models.DescriptionType.objects.filter(code=type_ref).exists():
                                type = models.DescriptionType.objects.get(code=type_ref)
                        except ValueError:
                            # exception to make wrong use of type ref right
                            if not description:
                                description = type_ref

                    # if rsr_type_ref:
                    #     if models.rsr_description_type.objects.filter(code=rsr_type_ref).exists():
                    #         rsr_type = models.rsr_description_type.objects.get(code=rsr_type_ref)



                    new_description = models.Description(activity=activity, description=description, type=type, language=language, rsr_description_type_id=rsr_type_ref)
                    new_description.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_activity_description")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_activity_description")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_activity_description")
        except Exception as e:
                    self.exception_handler(e, activity.id, "add_activity_description")


    def add_budget(self, elem, activity):
        try:
            for t in elem.xpath('budget'):

                try:
                    type_ref = self.return_first_exist(t.xpath( '@type' ))
                    type = None

                    period_start = self.return_first_exist(t.xpath( 'period-start/@iso-date'))
                    if not period_start:
                        period_start = self.return_first_exist(t.xpath('period-start/text()'))
                    period_end = self.return_first_exist(t.xpath( 'period-end/@iso-date'))
                    if not period_end:
                        period_end = self.return_first_exist(t.xpath('period-end/text()'))

                    value = self.return_first_exist(t.xpath( 'value/text()' ))
                    value_date = self.validate_date(self.return_first_exist(t.xpath('value/@value-date')))

                    currency_ref = self.return_first_exist(t.xpath('value/@currency'))
                    currency = None

                    if type_ref:
                        type_ref = type_ref.lower()
                        if type_ref == 'original':
                            type_ref = '1'
                        if type_ref == 'revised':
                            type_ref = '2'
                        if models.BudgetType.objects.filter(code=type_ref).exists():
                            type = models.BudgetType.objects.get(code=type_ref)

                    if currency_ref:
                        if models.Currency.objects.filter(code=currency_ref).exists():
                            currency = models.Currency.objects.get(code=currency_ref)

                    new_budget = models.Budget(activity=activity, type=type, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency)
                    new_budget.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_budget")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_budget")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_budget")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_budget")

        except Exception as e:
                self.exception_handler(e, activity.id, "add_budget")



    def add_planned_disbursement(self, elem, activity):

        try:
            for t in elem.xpath('planned-disbursement'):

                try:
                    period_start = self.return_first_exist(t.xpath( 'period_start/@iso-date'))
                    if not period_start:
                        period_start = self.return_first_exist(t.xpath('period_start/text()'))
                    period_end = self.return_first_exist(t.xpath( 'period_end/@iso-date'))
                    if not period_end:
                        period_end = self.return_first_exist(t.xpath('period_end/text()'))

                    value = self.return_first_exist(t.xpath( 'value/text()' ))
                    value_date = self.return_first_exist(t.xpath('value/@value-date'))
                    currency_ref = self.return_first_exist(t.xpath('value/@currency'))
                    currency = None

                    updated = self.return_first_exist(t.xpath('@updated'))

                    if currency_ref:
                        if models.Currency.objects.filter(code=currency_ref).exists():
                            currency = models.Currency.objects.get(code=currency_ref)

                    new_planned_disbursement = models.PlannedDisbursement(activity=activity, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency, updated=updated)
                    new_planned_disbursement.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_planned_disbursement")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_planned_disbursement")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_planned_disbursement")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_planned_disbursement")

        except Exception as e:
                self.exception_handler(e, activity.id, "add_planned_disbursement")

    # add many to 1
    def add_website(self, elem, activity):

        try:
            for t in elem.xpath('activity-website'):
                try:

                    url = self.return_first_exist(t.xpath( 'text()'))

                    new_website = models.ActivityWebsite(activity=activity, url=url)
                    new_website.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_website")

                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_website")

                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_website")

                except Exception as e:
                    self.exception_handler(e, activity.id, "add_website")

        except Exception as e:
            self.exception_handler(e, activity.id, "add_website")



    def add_contact_info(self, elem, activity):

        try:
            for t in elem.xpath('contact-info'):

                try:
                    person_name = self.return_first_exist(t.xpath('person-name/text()'))
                    organisation = self.return_first_exist(t.xpath('organisation/text()'))
                    telephone = self.return_first_exist(t.xpath('telephone/text()'))
                    email = self.return_first_exist(t.xpath('email/text()'))
                    mailing_address = self.return_first_exist(t.xpath('mailing-address/text()'))

                    type_ref = self.return_first_exist(t.xpath('@type'))
                    type = None

                    if type_ref:
                        if models.ContactType.objects.filter(code=type_ref).exists():
                            type = models.ContactType.objects.get(code=type_ref)

                    new_contact = models.ContactInfo(activity=activity, person_name=person_name, organisation=organisation, telephone=telephone, email=email, mailing_address=mailing_address, contact_type=type)
                    new_contact.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_contact_info")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_contact_info")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_contact_info")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_contact_info")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_contact_info")


    def add_transaction(self, elem, activity):

        try:

            for t in elem.xpath('transaction'):

                try:

                    ref = self.return_first_exist(t.xpath('@ref'))
                    aid_type_ref = self.return_first_exist(t.xpath('aid-type/@code'))
                    aid_type = None
                    description = self.return_first_exist(t.xpath('description/text()'))

                    description_type_ref = self.return_first_exist(t.xpath('description/@type'))
                    description_type = None
                    disbursement_channel_ref = self.return_first_exist(t.xpath('disbursement-channel/@code'))
                    disbursement_channel = None
                    finance_type_ref = self.return_first_exist(t.xpath('finance-type/@code'))
                    finance_type = None
                    flow_type_ref = self.return_first_exist(t.xpath('flow-type/@code'))
                    flow_type = None
                    provider_organisation_ref = self.return_first_exist(t.xpath('provider-org/@ref'))
                    provider_organisation = None
                    provider_organisation_name = self.return_first_exist(t.xpath('provider-org/text()'))
                    provider_activity = self.return_first_exist(t.xpath('provider-org/@provider-activity-id'))
                    receiver_organisation_ref = self.return_first_exist(t.xpath('receiver-org/@ref'))
                    receiver_organisation = None
                    receiver_organisation_name = self.return_first_exist(t.xpath('receiver-org/text()'))
                    tied_status_ref = self.return_first_exist(t.xpath('tied-status/@code'))
                    tied_status = None
                    transaction_date = self.validate_date(self.return_first_exist(t.xpath('transaction-date/@iso-date')))

                    transaction_type_ref = self.return_first_exist(t.xpath('transaction-type/@code'))
                    transaction_type = None
                    value = self.return_first_exist(t.xpath('value/text()'))

                    if value:
                        value = value.replace(",", "")

                    value_date = self.validate_date(self.return_first_exist(t.xpath('value/@value-date')))

                    currency_ref = self.return_first_exist(t.xpath('value/@currency'))
                    currency = None

                    if aid_type_ref:
                        aid_type_ref = aid_type_ref.replace("O", "0")
                        if models.AidType.objects.filter(code=aid_type_ref).exists():
                            aid_type = models.AidType.objects.get(code=aid_type_ref)
                    else:
                        aid_type = activity.default_aid_type

                    if description_type_ref:
                        if models.DescriptionType.objects.filter(code=description_type_ref).exists():
                            description_type = models.DescriptionType.objects.get(code=description_type_ref)

                    if disbursement_channel_ref:
                        if models.DisbursementChannel.objects.filter(code=disbursement_channel_ref).exists():
                            disbursement_channel = models.DisbursementChannel.objects.get(code=disbursement_channel_ref)

                    if finance_type_ref:
                        if models.FinanceType.objects.filter(code=finance_type_ref).exists():
                            finance_type = models.FinanceType.objects.get(code=finance_type_ref)
                    else:
                        finance_type = activity.default_finance_type

                    if flow_type_ref:
                        if models.FlowType.objects.filter(code=flow_type_ref).exists():
                            flow_type = models.FlowType.objects.get(code=flow_type_ref)
                    else:
                        flow_type = activity.default_flow_type

                    if provider_organisation_ref:
                        if models.Organisation.objects.filter(code=provider_organisation_ref).exists():
                            provider_organisation = models.Organisation.objects.get(code=provider_organisation_ref)
                        else:
                            provider_organisation_name_ref = self.return_first_exist(t.xpath('provider-org/text()'))

                            if models.Organisation.objects.filter(name=provider_organisation_name_ref).exists():
                                provider_organisation = models.Organisation.objects.filter(name=provider_organisation_name_ref)[0]
                            else:
                                provider_organisation_type = None
                                provider_organisation_type_ref = self.return_first_exist(t.xpath('provider-org/@type'))
                                if provider_organisation_type_ref:
                                    if models.OrganisationType.objects.filter(code=provider_organisation_type_ref).exists():
                                        provider_organisation_type = models.OrganisationType.objects.get(code=provider_organisation_type_ref)


                                try:

                                    new_organisation = models.Organisation(code=provider_organisation_ref, abbreviation=None, type=provider_organisation_type, reported_by_organisation=None, name=provider_organisation_name_ref)
                                    new_organisation.save()

                                except Exception as e:
                                    print '%s (%s)' % (e.message, type(e)) + " in add_transaction during adding provider organisation: " + activity.id


                    if receiver_organisation_ref:
                        if models.Organisation.objects.filter(code=receiver_organisation_ref).exists():
                            receiver_organisation = models.Organisation.objects.get(code=receiver_organisation_ref)
                        else:
                            receiver_organisation_name_ref = self.return_first_exist(t.xpath('receiver-org/text()'))

                            if models.Organisation.objects.filter(name=receiver_organisation_name_ref).exists():
                                receiver_organisation = models.Organisation.objects.filter(name=receiver_organisation_name_ref)[0]
                            else:

                                receiver_organisation_type = None
                                receiver_organisation_type_ref = self.return_first_exist(t.xpath('receiver-org/@type'))
                                if receiver_organisation_type_ref:
                                    if models.OrganisationType.objects.filter(code=receiver_organisation_type_ref).exists():
                                        receiver_organisation_type = models.OrganisationType.objects.get(code=receiver_organisation_type_ref)


                                try:

                                    new_organisation = models.Organisation(code=receiver_organisation_ref, abbreviation=None, type=receiver_organisation_type, reported_by_organisation=None, name=receiver_organisation_name_ref)
                                    new_organisation.save()

                                except Exception as e:
                                    print '%s (%s)' % (e.message, type(e)) + " in add_transaction during adding receiver organisation: " + activity.id


                    if tied_status_ref:
                        if models.TiedStatus.objects.filter(code=tied_status_ref).exists():
                            tied_status = models.TiedStatus.objects.get(code=tied_status_ref)
                    else:
                        tied_status = activity.default_tied_status

                    if transaction_type_ref:
                        if models.TransactionType.objects.filter(code=transaction_type_ref).exists():
                            transaction_type = models.TransactionType.objects.get(code=transaction_type_ref)

                    if currency_ref:
                        if models.Currency.objects.filter(code=currency_ref).exists():
                            currency = models.Currency.objects.get(code=currency_ref)
                    else:
                        currency = activity.default_currency


                    new_transaction = models.Transaction(activity=activity, aid_type=aid_type, description=description, description_type=description_type, disbursement_channel=disbursement_channel, finance_type=finance_type, flow_type=flow_type, provider_organisation=provider_organisation, provider_organisation_name=provider_organisation_name, provider_activity=provider_activity, receiver_organisation=receiver_organisation, receiver_organisation_name=receiver_organisation_name, tied_status=tied_status, transaction_date=transaction_date, transaction_type=transaction_type, value_date=value_date, value=value, ref=ref, currency=currency)
                    new_transaction.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_transaction")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_transaction")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_transaction")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_transaction")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_transaction")


    def add_result(self, elem, activity):

        try:
            for t in elem.xpath('result'):
                try:
                    type_ref = self.return_first_exist(t.xpath('@type'))
                    type = None
                    title = self.return_first_exist(t.xpath('title/text()'))
                    if title and title.__len__ > 255:
                        title = title[:255]
                    description = self.return_first_exist(t.xpath('description/text()'))

                    if type_ref:
                        type_ref = type_ref.lower()
                        if type_ref == 'output':
                            type_ref = '1'
                        if type_ref == 'outcome':
                            type_ref = '2'
                        if type_ref == 'impact':
                            type_ref == '3'
                        if self.isInt(type_ref) and models.ResultType.objects.filter(code=type_ref).exists():
                            type = models.ResultType.objects.get(code=type_ref)


                    new_result = models.Result(activity=activity, result_type=type, title=title, description=description)
                    new_result.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_result")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_result")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_result")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_result")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_result")

    # add many to many relationship
    def add_sectors(self, elem, activity):

        try:

            for t in elem.xpath('sector'):
                try:
                    sector_code = self.return_first_exist(t.xpath( '@code' ))
                    sector = None
                    vocabulary_code = self.return_first_exist(t.xpath('@vocabulary'))
                    vocabulary = None
                    percentage = self.return_first_exist(t.xpath('@percentage'))
                    if percentage:
                        percentage = percentage.replace("%", "")

                    if sector_code:
                        try:
                            int(sector_code)
                        except ValueError:
                            sector_code = None

                    if sector_code:
                        if models.Sector.objects.filter(code=sector_code).exists():
                            sector = models.Sector.objects.get(code=sector_code)

                    if not sector:
                        sector_name = self.return_first_exist(t.xpath( 'text()' ))
                        if models.Sector.objects.filter(name=sector_name).exists():
                            sector = models.Sector.objects.filter(name=sector_name)[0]

                    if vocabulary_code:
                        if models.Vocabulary.objects.filter(code=vocabulary_code).exists():
                            vocabulary = models.Vocabulary.objects.get(code=vocabulary_code)

                    if not sector:
                        alt_sector_name = sector_code
                    else:
                        alt_sector_name = None

                    new_activity_sector = models.ActivitySector(activity=activity, sector=sector,alt_sector_name=alt_sector_name, vocabulary=vocabulary, percentage = percentage)
                    new_activity_sector.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_sectors")
                    print  "in add_sectors: " + sector_code
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_sectors")
                    print  "in add_sectors: " + sector_code
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_sectors")
                    print  "in add_sectors: " + sector_code
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_sectors")

        except Exception as e:
            self.exception_handler(e, activity.id, "add_sectors")



    def add_countries(self, elem, activity):

        try:
            for t in elem.xpath('recipient-country'):
                try:
                    country_ref = self.return_first_exist(t.xpath( '@code' ))
                    country = None
                    percentage = self.return_first_exist(t.xpath('@percentage'))
                    if percentage:
                        percentage = percentage.replace("%", "")

                    if country_ref:
                        if models.Country.objects.filter(code=country_ref).exists():
                            country = models.Country.objects.get(code=country_ref)
                        elif country_ref == "KOS":
                            # Kosovo fix
                            country = models.Country.objects.get(code="XK")
                        else:
                            country_ref = country_ref.lower().capitalize()
                            if models.Country.objects.filter(name=country_ref).exists():
                                country = models.Country.objects.filter(name=country_ref)[0]
                    else:
                        continue

                    new_activity_country = models.ActivityRecipientCountry(activity=activity, country=country, percentage = percentage)
                    new_activity_country.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_countries")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_countries")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_countries")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_countries")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_countries")

    def add_regions(self, elem, activity):

        try:
            for t in elem.xpath('recipient-region'):

                region_ref = self.return_first_exist(t.xpath('@code'))
                region = None
                region_voc_ref = self.return_first_exist(t.xpath('@vocabulary'))
                region_voc = None
                percentage = self.return_first_exist(t.xpath('@percentage'))
                if percentage:
                        percentage = percentage.replace("%", "")

                if self.isInt(region_voc_ref):
                    if models.RegionVocabulary.objects.filter(code=region_voc_ref).exists():
                        region_voc = models.RegionVocabulary.objects.get(code=region_voc_ref)
                else:
                    region_voc = models.RegionVocabulary.objects.get(code=1)

                if region_ref:
                    if models.Region.objects.filter(code=region_ref).exists():
                        region = models.Region.objects.get(code=region_ref)
                    elif models.Region.objects.filter(name=region_ref).exists():
                            region = models.Region.objects.filter(name=region_ref)[0]
                    else:
                        print "error in add regions, unknown region: " + region_ref
                else:
                    continue

                try:
                    if not region:
                        print "Unknown region in add_regions: " + region_ref
                    else:
                        new_activity_region = models.ActivityRecipientRegion(activity=activity, region=region, percentage = percentage, region_vocabulary=region_voc)
                        new_activity_region.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_regions")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_regions")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_regions")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_regions")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_regions")


    def add_participating_organisations(self, elem, activity):


        try:
            for t in elem.xpath('participating-org'):

                try:
                    participating_organisation_ref = self.return_first_exist(t.xpath( '@ref' ))
                    participating_organisation = None

                    name = self.return_first_exist(t.xpath( 'text()' ))

                    role_ref = self.return_first_exist(t.xpath('@role'))
                    role = None

                    role_type = self.return_first_exist(t.xpath('@type'))
                    type = None

                    if role_type:
                        if self.isInt(role_type):
                            if models.OrganisationType.objects.filter(code=role_type).exists():
                                type = models.OrganisationType.objects.get(code=role_type)
                        else:
                            if models.OrganisationType.objects.filter(name=role_type).exists():
                                type = models.OrganisationType.objects.filter(name=role_type)[0]

                    if participating_organisation_ref:
                        if models.Organisation.objects.filter(code=participating_organisation_ref).exists():
                            participating_organisation = models.Organisation.objects.get(code=participating_organisation_ref)
                            if not participating_organisation.name:
                                participating_organisation.name = name
                            if not participating_organisation.type:
                                participating_organisation.type = type
                        else:
                            participating_organisation = models.Organisation(code=participating_organisation_ref, name=name, type=type)
                            participating_organisation.save()
                    else:
                        if name:
                            if models.Organisation.objects.filter(name=name).exists():

                                participating_organisation = models.Organisation.objects.filter(name=name)
                                participating_organisation = participating_organisation[0]

                    if role_ref:
                        if models.OrganisationRole.objects.filter(code=role_ref).exists():
                            role = models.OrganisationRole.objects.get(code=role_ref)

                    new_activity_participating_organisation = models.ActivityParticipatingOrganisation(activity=activity, organisation=participating_organisation, role=role, name=name)
                    new_activity_participating_organisation.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_participating_organisations")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_participating_organisations")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_participating_organisations")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_participating_organisations")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_participating_organisations")



    def add_policy_markers(self, elem, activity):

        try:
            for t in elem.xpath('policy-marker'):
                try:
                    policy_marker_code = self.return_first_exist(t.xpath( '@code' ))
                    alt_policy_marker = None
                    policy_marker = None
                    policy_marker_voc = self.return_first_exist(t.xpath( '@vocabulary' ))
                    vocabulary = None
                    policy_marker_significance = self.return_first_exist(t.xpath( '@significance' ))
                    significance = None

                    if policy_marker_code:
                        try:
                            int(policy_marker_code)
                        except ValueError:
                            alt_policy_marker = policy_marker_code
                            policy_marker_code = None


                    if policy_marker_code:
                        if models.PolicyMarker.objects.filter(code=policy_marker_code).exists():
                            policy_marker = models.PolicyMarker.objects.get(code=policy_marker_code)
                    else:
                        policy_marker_name = self.return_first_exist(t.xpath( 'text()' ))
                        if policy_marker_name:
                            if models.PolicyMarker.objects.filter(name=policy_marker_name).exists():
                                policy_marker = models.PolicyMarker.objects.get(code=policy_marker_name)

                    if policy_marker_voc:
                        if models.Vocabulary.objects.filter(code=policy_marker_voc).exists():
                            vocabulary = models.Vocabulary.objects.get(code=policy_marker_voc)

                    if policy_marker_significance:
                        if models.PolicySignificance.objects.filter(code=policy_marker_significance).exists():
                            significance = models.PolicySignificance.objects.get(code=policy_marker_significance)


                    new_activity_policy_marker = models.ActivityPolicyMarker(activity=activity, policy_marker=policy_marker, vocabulary=vocabulary, policy_significance=significance)
                    new_activity_policy_marker.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_policy_markers")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_policy_markers")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_policy_markers")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_policy_markers")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_policy_markers")


    def add_activity_date(self, elem, activity):

        try:

            for t in elem.xpath('activity-date'):

                try:
                    type_ref = self.return_first_exist(t.xpath( '@type' ))
                    type = None
                    curdate = self.return_first_exist(t.xpath( 'text()' ))
                    curdate = self.validate_date(curdate)

                    if not curdate:
                        curdate = self.return_first_exist(t.xpath( '@iso-date' ))
                        curdate = self.validate_date(curdate)



                    if type_ref:
                        if models.ActivityDateType.objects.filter(code=type_ref).exists():
                            type = models.ActivityDateType.objects.get(code=type_ref)
                        else:
                            type_ref = type_ref.lower();
                            type_ref = type_ref.replace(' ', '-');

                            if models.ActivityDateType.objects.filter(code=type_ref).exists():
                                type = models.ActivityDateType.objects.get(code=type_ref)


                    if type.code == 'end-actual':
                        activity.end_actual = curdate
                    if type.code == 'end-planned':
                        activity.end_planned = curdate
                    if type.code == 'start-actual':
                        activity.start_actual = curdate
                    if type.code == 'start-planned':
                        activity.start_planned = curdate

                    activity.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_activity_date")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_activity_date")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_activity_date")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_activity_date")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_activity_date")


    def add_related_activities(self, elem, activity):

        try:
            for t in elem.xpath('related-activity'):

                try:
                    type_ref = self.return_first_exist(t.xpath( '@type' ))
                    type = None
                    ref = self.return_first_exist(t.xpath('@ref'))
                    text = self.return_first_exist(t.xpath('text()'))

                    if type_ref:
                        if self.isInt(type_ref) and models.RelatedActivityType.objects.filter(code=type_ref).exists():
                            type = models.RelatedActivityType.objects.get(code=type_ref)
                        else:
                            type_ref = type_ref.lower().capitalize()
                            if models.RelatedActivityType.objects.filter(name=type_ref).exists():
                                type = models.RelatedActivityType.objects.filter(name=type_ref)[0]

                    new_related_activity = models.RelatedActivity(current_activity=activity, type=type, ref=ref, text=text)
                    new_related_activity.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_related_activities")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_related_activities")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_related_activities")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_related_activities")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_related_activities")


    def add_location(self, elem, activity):

        try:
            for t in elem.xpath('location'):

                try:
                    name = self.return_first_exist(t.xpath('name/text()'))
                    type_ref = self.return_first_exist(t.xpath('location-type/@code'))
                    type = None
                    type_description = self.return_first_exist(t.xpath('location-type/text()'))
                    description = self.return_first_exist(t.xpath('description/text()'))
                    description_type_ref = self.return_first_exist(t.xpath('description/@type'))
                    description_type = None
                    adm_country_iso_ref = self.return_first_exist(t.xpath('administrative/@country'))
                    adm_country_iso = None
                    adm_country_adm1 = self.return_first_exist(t.xpath('administrative/@adm1'))
                    adm_country_adm2 = self.return_first_exist(t.xpath('administrative/@adm2'))
                    adm_country_name = self.return_first_exist(t.xpath('administrative/text()'))
                    percentage = self.return_first_exist(t.xpath('@percentage'))
                    latitude = self.return_first_exist(t.xpath('coordinates/@latitude'))
                    longitude = self.return_first_exist(t.xpath('coordinates/@longitude'))
                    precision_ref = self.return_first_exist(t.xpath('coordinates/@precision'))
                    precision = None
                    gazetteer_entry = self.return_first_exist(t.xpath('gazetteer-entry/text()'))
                    gazetteer_ref_ref = self.return_first_exist(t.xpath('gazetteer-entry/@gazetteer-ref'))
                    gazetteer_ref = None

                    if type_ref:
                        if models.LocationType.objects.filter(code=type_ref).exists():
                            type = models.LocationType.objects.get(code=type_ref)

                    if description_type_ref:
                        if models.DescriptionType.objects.filter(code=description_type_ref).exists():
                            description_type = models.DescriptionType.objects.get(code=description_type_ref)

                    if adm_country_iso_ref:
                        if models.Country.objects.filter(code=adm_country_iso_ref).exists():
                            adm_country_iso = models.Country.objects.get(code=adm_country_iso_ref)

                    if precision_ref:
                        if models.GeographicalPrecision.objects.filter(code=precision_ref).exists():
                            precision = models.GeographicalPrecision.objects.get(code=precision_ref)

                    if gazetteer_ref_ref:
                        if models.GazetteerAgency.objects.filter(code=gazetteer_ref_ref).exists():
                            gazetteer_ref = models.GazetteerAgency.objects.get(code=gazetteer_ref_ref)


                    new_location = models.Location(activity=activity, name=name, type=type, type_description=type_description, description=description, description_type=description_type, adm_country_iso=adm_country_iso, adm_country_adm1=adm_country_adm1, adm_country_adm2=adm_country_adm2, adm_country_name=adm_country_name, percentage=percentage, latitude=latitude, longitude=longitude, precision=precision, gazetteer_entry=gazetteer_entry, gazetteer_ref=gazetteer_ref)
                    new_location.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_location")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_location")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_location")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_location")
        except Exception as e:
                self.exception_handler(e, activity.id, "add_location")

    def add_conditions(self, elem, activity):

        try:
            for t in elem.xpath('conditions/condition'):

                try:
                    condition_type_ref = self.return_first_exist(t.xpath('@type'))
                    condition_type = None
                    condition = self.return_first_exist(t.xpath('text()'))

                    if condition_type_ref:
                        if models.ConditionType.objects.filter(code=condition_type_ref).exists():
                            condition_type = models.ConditionType.objects.get(code=condition_type_ref)

                    new_condition = models.Condition(activity=activity, text=condition, type=condition_type)
                    new_condition.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_conditions")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_conditions")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_conditions")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_conditions")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_conditions")


    def add_document_link(self, elem, activity):

        try:
            for t in elem.xpath('document-link'):

                try:
                    url = self.return_first_exist(t.xpath('@url'))
                    file_format_ref = self.return_first_exist(t.xpath('@format'))
                    file_format = None
                    title = self.return_first_exist(t.xpath('title/text()'))
                    # doc_category_text = self.return_first_exist(t.xpath('category/text()'))
                    doc_category_ref = self.return_first_exist(t.xpath('category/@code'))
                    doc_category = None
                    # language_ref = self.return_first_exist(t.xpath('language/@code'))
                    # language = None



                    if file_format_ref:
                        if models.FileFormat.objects.filter(code=file_format_ref).exists():
                            file_format = models.FileFormat.objects.get(code=file_format_ref)

                    if doc_category_ref:
                        if models.DocumentCategory.objects.filter(code=doc_category_ref).exists():
                            doc_category = models.DocumentCategory.objects.get(code=doc_category_ref)

                    # if language_ref:
                    #     if models.language.objects.filter(code=language_ref).exists():
                    #         language = models.language.objects.get(code=language_ref)



                    document_link = models.DocumentLink(activity=activity, url=url, file_format=file_format, document_category=doc_category)
                    document_link.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_document_link")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_document_link")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_document_link")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_document_link")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_document_link")




    def add_country_budget_items(self, elem, activity):

        try:
            for t in elem.xpath('country-budget-items'):
                try:
                    budget_identifier_vocabulary_ref = self.return_first_exist(t.xpath('@vocabulary'))
                    budget_identifier_vocabulary = None
                    if budget_identifier_vocabulary_ref and self.isInt(budget_identifier_vocabulary_ref):
                        if models.BudgetIdentifierVocabulary.objects.filter(code=budget_identifier_vocabulary_ref).exists():
                            budget_identifier_vocabulary = models.BudgetIdentifierVocabulary.objects.get(code=budget_identifier_vocabulary_ref)

                    for bi in elem.xpath('budget-item'):

                        code_ref = self.return_first_exist(bi.xpath('@code'))
                        code = None
                        percentage = self.return_first_exist(bi.xpath('@percentage'))
                        description = self.return_first_exist(bi.xpath('description/text()'))

                        if code_ref:
                            if models.BudgetIdentifier.objects.filter(code=code_ref).exists():
                                code = models.BudgetIdentifier.objects.get(code=code_ref)

                        country_budget_item = models.CountryBudgetItem(activity=activity, vocabulary=budget_identifier_vocabulary, code=code, percentage=percentage, description=description)
                        country_budget_item.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_country_budget_items")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_country_budget_items")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_country_budget_items")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_country_budget_items")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_country_budget_items")



    def add_crs_add(self, elem, activity):

        try:
            for t in elem.xpath('crs-add'):
                try:

                    aid_type_flag_ref = self.return_first_exist(t.xpath('aidtype-flag/@code'))
                    aid_type_flag_significance = self.return_first_exist(t.xpath('aidtype-flag/@significance'))
                    aid_type_flag = None

                    if aid_type_flag_ref:
                            if models.AidTypeFlag.objects.filter(code=aid_type_flag_ref).exists():
                                aid_type_flag = models.AidTypeFlag.objects.get(code=aid_type_flag_ref)

                    new_crs_add = models.CrsAdd(aid_type_flag=aid_type_flag, aid_type_flag_significance=aid_type_flag_significance)
                    new_crs_add.save()

                    for lt in elem.xpath('loan-terms'):

                        rate_1 = self.return_first_exist(lt.xpath('@rate-1'))
                        rate_2 = self.return_first_exist(lt.xpath('@rate-2'))
                        repayment_type_ref = self.return_first_exist(lt.xpath('repayment-type/@code'))
                        repayment_type = None
                        repayment_plan_ref = self.return_first_exist(lt.xpath('repayment-plan/@code'))
                        repayment_plan = None
                        repayment_plan_text = self.return_first_exist(lt.xpath('repayment-plan/text()'))
                        commitment_date = self.return_first_exist(lt.xpath('commitment-date/@iso-date'))
                        repayment_first_date = self.return_first_exist(lt.xpath('repayment-first-date/@iso-date'))
                        repayment_final_date = self.return_first_exist(lt.xpath('repayment-final-date/@iso-date'))

                        if repayment_type_ref:
                            if models.LoanRepaymentType.objects.filter(code=repayment_type_ref).exists():
                                repayment_type = models.LoanRepaymentType.objects.get(code=repayment_type_ref)

                        if repayment_plan_ref:
                            if models.LoanRepaymentPeriod.objects.filter(code=repayment_plan_ref).exists():
                                repayment_plan = models.LoanRepaymentPeriod.objects.get(code=repayment_plan_ref)

                        new_loan_term = models.CrsAddLoanTerms(crs_add=new_crs_add, rate_1=rate_1, rate_2=rate_2, repayment_type=repayment_type, repayment_plan=repayment_plan, repayment_plan_text=repayment_plan_text, commitment_date=commitment_date, repayment_first_date=repayment_first_date, repayment_final_date=repayment_final_date)
                        new_loan_term.save()

                    for ls in elem.xpath('loan-status'):

                        year = self.return_first_exist(ls.xpath(''))
                        value_date = self.return_first_exist(ls.xpath(''))
                        currency_ref = self.return_first_exist(ls.xpath(''))
                        currency = None
                        interest_received = self.return_first_exist(ls.xpath(''))
                        principal_outstanding = self.return_first_exist(ls.xpath(''))
                        principal_arrears = self.return_first_exist(ls.xpath(''))
                        interest_arrears = self.return_first_exist(ls.xpath(''))

                        if currency_ref:
                            if models.Currency.objects.filter(code=currency_ref).exists():
                                currency = models.Currency.objects.get(code=currency_ref)

                        new_loan_status = models.CrsAddLoanStatus(crs_add=new_crs_add, year=year, value_date=value_date, currency=currency, interest_received=interest_received, principal_outstanding=principal_outstanding, principal_arrears=principal_arrears, interest_arrears=interest_arrears)
                        new_loan_status.save()


                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_crs_add")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_crs_add")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_crs_add")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_crs_add")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_crs_add")



    def add_fss(self, elem, activity):

        try:
            for t in elem.xpath('ffs'):
                try:
                    extraction_date = self.return_first_exist(t.xpath('@extraction-date'))
                    priority = self.return_first_exist(t.xpath('@priority'))
                    phaseout_year = self.return_first_exist(t.xpath('@phaseout-year'))

                    new_ffs = models.Ffs(activity=activity, extraction_date=extraction_date, priority=priority, phaseout_year=phaseout_year)
                    new_ffs.save()

                    for fc in elem.xpath('forecast'):
                        year = self.return_first_exist(fc.xpath('@year'))
                        currency_ref = self.return_first_exist(fc.xpath('@currency'))
                        currency = None
                        value_date = self.return_first_exist(fc.xpath('@value-date'))
                        value = self.return_first_exist(fc.xpath('text()'))

                        if currency_ref:
                            if models.Currency.objects.filter(code=currency_ref).exists():
                                currency = models.Currency.objects.get(code=currency_ref)

                        new_forecast = models.FfsForecast(ffs=new_ffs, year=year, currency=currency, value_date=value_date, value=value)
                        new_forecast.save()

                except IntegrityError, e:
                    self.exception_handler(e, activity.id, "add_fss")
                except ValueError, e:
                    self.exception_handler(e, activity.id, "add_fss")
                except ValidationError, e:
                    self.exception_handler(e, activity.id, "add_fss")
                except Exception as e:
                    self.exception_handler(e, activity.id, "add_fss")
        except Exception as e:
            self.exception_handler(e, activity.id, "add_fss")


    def add_total_budget(self, activity):

        try:
            updater = TotalBudgetUpdater()
            updater.update_single_activity(activity.id)
        except Exception as e:
            self.exception_handler(e, activity.id, "add_total_budget")
