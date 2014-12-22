from lxml import etree
from iati import models
from iati.management.commands.total_budget_updater import TotalBudgetUpdater
from re import sub
from django.conf import settings
import time
from datetime import datetime
from deleter import Deleter
import gc
from iati.filegrabber import FileGrabber
from iati_synchroniser.exception_handler import exception_handler
from iati.data_backup.unesco_sectors import unesco_sectors
import string
import random



class Parser():

    xml_source_ref = None

    def parse_url(self, url, xml_source_ref):

        try:
            #iterate through iati-activity tree
            file_grabber = FileGrabber()
            iati_file = file_grabber.get_the_file(url)
            if iati_file:

                # delete old activities
                try:
                    deleter = Deleter()
                    deleter.delete_by_source(xml_source_ref)
                except Exception as e:
                    exception_handler(e, "parse url", "delete by source")

                # parse the new file
                self.xml_source_ref = xml_source_ref
                context = etree.iterparse(iati_file, tag='iati-activity')
                self.fast_iter(context, self.process_element)

                del iati_file
                gc.collect()

                # Throw away query logs when in debug mode to prevent memory from overflowing
                if settings.DEBUG:
                    from django import db
                    db.reset_queries()

        except Exception as e:
            exception_handler(e, "parse url", "parse_url")

    # loop through the activities, fast_iter starts at the last activity and walks towards the first
    def fast_iter(self, context, func):

        try:

            for event, elem in context:

                try:
                    func(elem)
                except Exception as e:
                    exception_handler(e, "fast_iter", "fast_iter")
                elem.clear()

                # for ancestor in elem.xpath('ancestor-or-self::*'):
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
            del context
        except Exception as e:
            exception_handler(e, "fast_iter", "fast_iter")



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
            if activity:
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

                # V1.04
                self.add_country_budget_items(elem, activity)
                self.add_crs_add(elem, activity)
                self.add_fss(elem, activity)


                # ManyToMany
                self.add_sectors(elem, activity)
                self.add_participating_organisations(elem, activity)
                self.add_countries(elem, activity)
                self.add_regions(elem, activity)
                self.add_policy_markers(elem, activity)
                self.add_activity_date(elem, activity)

                # Extras
                self.add_total_budget(activity)
                self.add_activity_search_data(activity)

        except Exception as e:
                exception_handler(e, iati_identifier, "add_all_activity_data")


    # class wide functions
    def return_first_exist(self, xpath_find):

        if not xpath_find:
             xpath_find = None
        else:
            try:
                xpath_find = unicode(xpath_find[0], errors='ignore')
            except:
                xpath_find = xpath_find[0]

            xpath_find = xpath_find.encode('utf-8', 'ignore')
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
            unvalidated_date = unvalidated_date.strip(' \t\n\r')

        if unvalidated_date:
            try:
                unvalidated_date = unvalidated_date.split("Z")[0]
                unvalidated_date = sub(r'[\t]', '', unvalidated_date)
                unvalidated_date = unvalidated_date.replace(" ", "")
                unvalidated_date = unvalidated_date.replace("/", "-")
                if len(unvalidated_date) == 4:
                    unvalidated_date = unvalidated_date + "-01-01"
                try:
                    validated_date = time.strptime(unvalidated_date, '%Y-%m-%d')
                except ValueError:
                    validated_date = time.strptime(unvalidated_date, '%d-%m-%Y')
                valid_date = datetime.fromtimestamp(time.mktime(validated_date))

            except ValueError:
                # if not any(c.isalpha() for c in unvalidated_date):
                #     exception_handler(None, "validate_date", 'Invalid date: ' + unvalidated_date)
                return None
            except Exception as e:
                exception_handler(e, "validate date", "validate_date")
                return None
        return valid_date


    def activity_exists(self, elem):

        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))

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


    # entity add functions
    def add_organisation(self, elem):
        try:
            ref = self.return_first_exist(elem.xpath('reporting-org/@ref'))
            type_ref = self.return_first_exist(elem.xpath('reporting-org/@type'))
            name = self.return_first_exist(elem.xpath('reporting-org/text()'))

            self.find_or_create_organisation(ref, name, type_ref)

        except Exception as e:
            exception_handler(e, ref, "add_organisation")



    def add_activity(self, elem):
        try:
            iati_identifier = self.return_first_exist(elem.xpath('iati-identifier/text()'))
            iati_identifier = iati_identifier.strip(' \t\n\r')
            activity_id = iati_identifier.replace("/", "-")
            activity_id = activity_id.replace(":", "-")
            activity_id = activity_id.replace(" ", "")



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

            secondary_publisher = self.return_first_exist(elem.xpath('reporting-org/@secondary-publisher'))

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

            if not secondary_publisher:
                secondary_publisher = False


            if activity_scope_ref and self.isInt(activity_scope_ref):
                if models.ActivityScope.objects.filter(code=activity_scope_ref).exists():
                    activity_scope = models.ActivityScope.objects.get(code=activity_scope_ref)

            new_activity = models.Activity(id=activity_id, default_currency=default_currency, hierarchy=hierarchy, last_updated_datetime=last_updated_datetime, linked_data_uri=linked_data_uri, reporting_organisation=reporting_organisation, secondary_publisher=secondary_publisher, activity_status=activity_status, collaboration_type=collaboration_type, default_flow_type=default_flow_type, default_aid_type=default_aid_type, default_finance_type=default_finance_type, default_tied_status=default_tied_status, xml_source_ref=self.xml_source_ref, iati_identifier=iati_identifier, iati_standard_version=iati_standard_version, capital_spend=capital_spend, scope=activity_scope)
            new_activity.save()
            return new_activity

        except Exception as e:
            exception_handler(e, activity_id, "add_activity")


    #after activity is added

    # add one to many
    def add_other_identifier(self, elem, activity):

        try:
            for t in elem.xpath('other-identifier'):

                try:
                    owner_ref = self.return_first_exist(t.xpath( '@owner-ref' ))
                    owner_name = self.return_first_exist(t.xpath( '@owner-name' ))
                    other_identifier = self.return_first_exist(t.xpath( 'text()' ))
                    if not other_identifier:
                        other_identifier = " "
                    new_other_identifier = models.OtherIdentifier(activity=activity, owner_ref=owner_ref, owner_name=owner_name, identifier=other_identifier)
                    new_other_identifier.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_other_identifier")
        except Exception as e:
                    exception_handler(e, activity.id, "add_other_identifier")



    def add_activity_title(self, elem, activity):

        try:
            for t in elem.xpath('title'):
                try:
                    title = self.return_first_exist(t.xpath('text()'))
                    if title:

                        language_ref = self.return_first_exist(t.xpath('@xml:lang'))
                        language = None
                        if title.__len__() > 255:
                            title = title[:255]

                        if language_ref:
                            if models.Language.objects.filter(code=language_ref).exists():
                                language = models.Language.objects.get(code=language_ref)


                        new_title = models.Title(activity=activity, title=title, language=language)
                        new_title.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_activity_title")

        except Exception as e:
            exception_handler(e, activity.id, "add_activity_title")



    def add_activity_description(self, elem, activity):

        try:
            for t in elem.xpath('description'):
                try:
                    description = self.return_first_exist(t.xpath('text()'))
                    type_ref = self.return_first_exist(t.xpath('@type'))
                    type = None
                    language_ref = self.return_first_exist(t.xpath('@xml:lang'))
                    language = None
                    rsr_type_ref = self.return_first_exist(t.xpath('@akvo:type', namespaces={'akvo': 'http://akvo.org/api/v1/iati-activities'}))
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

                    if not description:
                        continue

                    # if rsr_type_ref:
                    #     if models.rsr_description_type.objects.filter(code=rsr_type_ref).exists():
                    #         rsr_type = models.rsr_description_type.objects.get(code=rsr_type_ref)

                    # RAIN exceptions
                    if activity.reporting_organisation_id == "NL-KVK-34200988":

                        rain_type = self.return_first_exist(t.xpath('@rain:type', namespaces={'rain': 'http://data.rainfoundation.org'}))

                        lookuplist = {}

                        if rain_type == "d_context":

                            type = models.DescriptionType.objects.get(name=rain_type)
                            new_description = models.Description(activity=activity, description=description, type=type, language=language, rsr_description_type_id=rsr_type_ref)
                            new_description.save()
                            continue

                        if rain_type == "services": # rain_services
                            lookuplist = {'ADV': 'Advice', 'INT': 'Intelligence', 'IMP': 'Implementation'}
                        if rain_type == "type": # cat rain_project_type
                            lookuplist = {'CAP': 'Capacity Development', 'R-D': 'Research and Development', 'L-P': 'Lobby and Promotion', 'INF': 'Infrastructure'}
                        if rain_type == "d_themes": # cat rain_themes
                            lookuplist = {'WASH': 'WASH', '3R': '3R', 'MUS': 'MUS', 'BDEV': 'Business Development', 'FSEC': 'Food Security', 'OTH': 'Other'}
                        if rain_type == "d_subjects": # cat rain_sustainability
                            lookuplist = {'F': 'Financial', 'I': 'Institutional', 'E': 'Environmental', 'T': 'Technical', 'S': 'Social'}

                        if rain_type in ['services', 'type', 'd_themes', 'd_subjects']:
                            splitted_sectors = description.split(",")
                            for sec in splitted_sectors:
                                if sec in lookuplist:
                                    secname = lookuplist[sec]
                                    sector = models.Sector.objects.get(name=secname)
                                    new_activity_sector = models.ActivitySector(activity=activity, sector=sector,alt_sector_name=None, vocabulary=None, percentage=None)
                                    new_activity_sector.save()


                    new_description = models.Description(activity=activity, description=description, type=type, language=language, rsr_description_type_id=rsr_type_ref)
                    new_description.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_activity_description")
        except Exception as e:
                    exception_handler(e, activity.id, "add_activity_description")


    def add_budget(self, elem, activity):
        try:
            for t in elem.xpath('budget'):

                try:
                    type_ref = self.return_first_exist(t.xpath( '@type' ))
                    type = None

                    period_start = self.return_first_exist(t.xpath( 'period-start/@iso-date'))
                    if not period_start:
                        period_start = self.return_first_exist(t.xpath('period-start/text()'))
                    period_start = self.validate_date(period_start)

                    period_end = self.return_first_exist(t.xpath( 'period-end/@iso-date'))
                    if not period_end:
                        period_end = self.return_first_exist(t.xpath('period-end/text()'))
                    period_end = self.validate_date(period_end)

                    value = self.return_first_exist(t.xpath('value/text()'))

                    if value:
                        value = value.strip(' \t\n\r')
                    if value:
                        value = value.replace(",", ".")
                        value = value.replace(" ", "")
                    else:
                        continue

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

                    if not value:
                        continue

                    # RAIN SPECIFIC
                    if activity.reporting_organisation_id == "NL-KVK-34200988":

                        # save budget per rain type
                        for curvalue in t.xpath('value'):

                            value = self.return_first_exist(curvalue.xpath('text()'))
                            rain_type = self.return_first_exist(curvalue.xpath('@rain:type', namespaces={'rain': 'http://data.rainfoundation.org'}))

                            if models.BudgetType.objects.filter(name=rain_type).exists():

                                budget_type = models.BudgetType.objects.get(name=rain_type)
                                new_budget = models.Budget(activity=activity, type=budget_type, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency)
                                new_budget.save()
                        continue


                    new_budget = models.Budget(activity=activity, type=type, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency)
                    new_budget.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_budget")

        except Exception as e:
                exception_handler(e, activity.id, "add_budget")



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


                except Exception as e:
                    exception_handler(e, activity.id, "add_planned_disbursement")

        except Exception as e:
                exception_handler(e, activity.id, "add_planned_disbursement")

    # add many to 1
    def add_website(self, elem, activity):

        try:
            for t in elem.xpath('activity-website'):
                try:

                    url = self.return_first_exist(t.xpath( 'text()'))
                    if url:
                        new_website = models.ActivityWebsite(activity=activity, url=url)
                        new_website.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_website")

        except Exception as e:
            exception_handler(e, activity.id, "add_website")



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

                    if self.isInt(type_ref):
                        if models.ContactType.objects.filter(code=type_ref).exists():
                            type = models.ContactType.objects.get(code=type_ref)

                    new_contact = models.ContactInfo(activity=activity, person_name=person_name, organisation=organisation, telephone=telephone, email=email, mailing_address=mailing_address, contact_type=type)
                    new_contact.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_contact_info")
        except Exception as e:
                exception_handler(e, activity.id, "add_contact_info")


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
                        value = value.strip(' \t\n\r')
                    # if value:
                    #     value = value.replace(",", ".")
                    #     value = value.replace(" ", "")
                    #     if value.__len__() > 2:
                    #         dec = False
                    #         if value[-2] == ".":
                    #             dec = True
                    #         value = value.replace(".", "")
                    #         if dec:
                    #             value = value[:-2] + "." + value[-2:]
                    # else:
                    #     continue

                    if not value:
                        continue

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

                    if self.isInt(flow_type_ref):
                        if models.FlowType.objects.filter(code=flow_type_ref).exists():
                            flow_type = models.FlowType.objects.get(code=flow_type_ref)
                    elif flow_type_ref:
                        if models.FlowType.objects.filter(name=flow_type_ref).exists():
                            flow_type = models.FlowType.objects.get(name=flow_type_ref)
                    else:
                        flow_type = activity.default_flow_type


                    provider_organisation = self.find_or_create_organisation(provider_organisation_ref, provider_organisation_name)
                    receiver_organisation = self.find_or_create_organisation(receiver_organisation_ref, receiver_organisation_name)


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


                except Exception as e:
                    exception_handler(e, activity.id, "add_transaction")
                    if value:
                        exception_handler(e, "and value is", value)
        except Exception as e:
            exception_handler(e, activity.id, "add_transaction")


    def org_key_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def find_or_create_organisation(self, ref, org_name, type_ref=None):

        # possibilities :
        # ref and name, exists
        # ref and name, does not exist
        # ref no name, exists
        # ref no name, does not exist
        # no ref, has name, exists
        # no ref, has name, does not exist
        # no ref, no name

        try:

            if ref:
                ref = ref.strip()
            # no ref, no name
            if not ref and not org_name:
                return None
            # no ref, has name, exists
            # no ref, has name, does not exist
            if not ref:
                ref = "u"

            # ref and name, exists
            if models.Organisation.objects.filter(code=ref).exists() and org_name:
                if models.Organisation.objects.filter(name=org_name, original_ref=ref).exists():
                    found_org = models.Organisation.objects.filter(name=org_name, original_ref=ref)[0]
                else:
                    for x in range(0, 10):
                        random_key = self.org_key_generator()

                        temp_ref = ref + "-" + random_key
                        if models.Organisation.objects.filter(code=temp_ref).exists():
                                continue
                        else:
                            found_org = models.Organisation(code=temp_ref, name=org_name, type=None, original_ref=ref)
                            found_org.save()
                            break
            # ref no name, exists
            elif models.Organisation.objects.filter(code=ref, name=None).exists():
                #org with no name, if found get, else create new org
                found_org = models.Organisation.objects.filter(code=ref, name=None)[0]

            # ref and name, does not exist,
            # ref no name, does not exist
            else:

                if type_ref:
                    if self.isInt(type_ref):
                        if models.OrganisationType.objects.filter(code=type_ref).exists():
                            org_type = models.OrganisationType.objects.get(code=type_ref)
                    elif models.OrganisationType.objects.filter(name=type_ref).exists():
                        org_type = models.OrganisationType.objects.filter(name=type_ref)[0]
                    else:
                        org_type = None

                found_org = models.Organisation(code=ref, name=org_name, type=None, original_ref=ref)
                found_org.save()

            return found_org

        except Exception as e:
            exception_handler(e, ref, "find_or_create_organisation")

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
                            type_ref = '3'
                        if self.isInt(type_ref) and models.ResultType.objects.filter(code=type_ref).exists():
                            type = models.ResultType.objects.get(code=type_ref)


                    new_result = models.Result(activity=activity, result_type=type, title=title, description=description)
                    new_result.save()

                except Exception as e:
                    exception_handler(e, activity.id, "add_result")
        except Exception as e:
            exception_handler(e, activity.id, "add_result")

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

                    if not self.isInt(sector_code):

                        if sector_code in unesco_sectors:
                            sector_code = unesco_sectors[sector_code]
                        else:
                            sector_code = None

                    if sector_code:
                        if models.Sector.objects.filter(code=sector_code).exists():
                            sector = models.Sector.objects.get(code=sector_code)

                    if not sector:
                        sector_name = self.return_first_exist(t.xpath('text()'))
                        if models.Sector.objects.filter(name=sector_name).exists():
                            sector = models.Sector.objects.filter(name=sector_name)[0]

                    if vocabulary_code:
                        if models.Vocabulary.objects.filter(code=vocabulary_code).exists():
                            vocabulary = models.Vocabulary.objects.get(code=vocabulary_code)

                    if not sector:
                        alt_sector_name = sector_code
                    else:
                        alt_sector_name = None

                    new_activity_sector = models.ActivitySector(activity=activity, sector=sector,alt_sector_name=alt_sector_name, vocabulary=vocabulary, percentage=percentage)
                    new_activity_sector.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_sectors")
        except Exception as e:
            exception_handler(e, activity.id, "add_sectors")



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
                        elif country_ref == "KOS" or country_ref == "KS":
                            # Kosovo fix
                            country = models.Country.objects.get(code="XK")
                        else:
                            country_ref = country_ref.lower().capitalize()
                            if models.Country.objects.filter(name=country_ref).exists():
                                country = models.Country.objects.filter(name=country_ref)[0]
                    else:
                        continue

                    if country:
                        new_activity_country = models.ActivityRecipientCountry(activity=activity, country=country, percentage = percentage)
                        new_activity_country.save()
                    # else:
                    #     exception_handler(None, activity.id, "add_countries, country not found: " + country_ref)


                except Exception as e:
                    exception_handler(e, activity.id, "add_countries, country = " + country_ref)
        except Exception as e:
                exception_handler(e, activity.id, "add_countries")

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

                if self.isInt(region_ref):
                    if models.Region.objects.filter(code=region_ref).exists():
                        region = models.Region.objects.get(code=region_ref)
                    elif models.Region.objects.filter(name=region_ref).exists():
                            region = models.Region.objects.filter(name=region_ref)[0]
                    else:
                        region = None
                else:
                    continue

                try:
                    if not region:
                        continue
                        # exception_handler(None, "add_regions", "Unknown region: " + region_ref)
                    else:
                        new_activity_region = models.ActivityRecipientRegion(activity=activity, region=region, percentage = percentage, region_vocabulary=region_voc)
                        new_activity_region.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_regions")
        except Exception as e:
                exception_handler(e, activity.id, "add_regions")


    def add_participating_organisations(self, elem, activity):


        try:
            for t in elem.xpath('participating-org'):

                try:
                    participating_organisation_ref = self.return_first_exist(t.xpath('@ref'))
                    name = self.return_first_exist(t.xpath('text()'))

                    participating_organisation = self.find_or_create_organisation(participating_organisation_ref, name)

                    role_ref = self.return_first_exist(t.xpath('@role'))
                    role = None

                    if role_ref:
                        if models.OrganisationRole.objects.filter(code=role_ref).exists():
                            role = models.OrganisationRole.objects.get(code=role_ref)

                    new_activity_participating_organisation = models.ActivityParticipatingOrganisation(activity=activity, organisation=participating_organisation, role=role, name=name)
                    new_activity_participating_organisation.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_participating_organisations")
        except Exception as e:
                exception_handler(e, activity.id, "add_participating_organisations")



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


                    if self.isInt(policy_marker_code):
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

                    if self.isInt(policy_marker_significance):
                        if models.PolicySignificance.objects.filter(code=policy_marker_significance).exists():
                            significance = models.PolicySignificance.objects.get(code=policy_marker_significance)


                    new_activity_policy_marker = models.ActivityPolicyMarker(activity=activity, policy_marker=policy_marker, vocabulary=vocabulary, policy_significance=significance)
                    new_activity_policy_marker.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_policy_markers")
        except Exception as e:
                exception_handler(e, activity.id, "add_policy_markers")


    def add_activity_date(self, elem, activity):

        try:

            for t in elem.xpath('activity-date'):

                try:
                    type_ref = self.return_first_exist(t.xpath('@type'))
                    type = None
                    curdate = self.return_first_exist(t.xpath('@iso-date'))
                    curdate = self.validate_date(curdate)

                    if not curdate:
                        curdate = self.return_first_exist(t.xpath('text()'))
                        curdate = self.validate_date(curdate)

                    if type_ref:
                        if models.ActivityDateType.objects.filter(code=type_ref).exists():
                            type = models.ActivityDateType.objects.get(code=type_ref)
                        else:
                            type_ref = type_ref.lower()
                            type_ref = type_ref.replace(' ', '-')
                            if models.ActivityDateType.objects.filter(code=type_ref).exists():
                                type = models.ActivityDateType.objects.get(code=type_ref)

                    if not type:
                        continue

                    if not curdate:
                        continue

                    if type.code == 'end-actual':
                        activity.end_actual = curdate
                    if type.code == 'end-planned':
                        activity.end_planned = curdate
                    if type.code == 'start-actual':
                        activity.start_actual = curdate
                    if type.code == 'start-planned':
                        activity.start_planned = curdate

                    activity.save()


                except Exception as e:
                    exception_handler(e, activity.id, "add_activity_date")
        except Exception as e:
                exception_handler(e, activity.id, "add_activity_date")


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

                except Exception as e:
                    exception_handler(e, activity.id, "add_related_activities")
        except Exception as e:
            exception_handler(e, activity.id, "add_related_activities")


    def add_location(self, elem, activity):

        try:
            for t in elem.xpath('location'):

                try:
                    ref = self.return_first_exist(t.xpath('@ref'))
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
                    percentage = self.return_first_exist(t.xpath('@percentage')) # Deprecated since 1.04
                    latitude = self.return_first_exist(t.xpath('coordinates/@latitude'))
                    longitude = self.return_first_exist(t.xpath('coordinates/@longitude'))
                    precision_ref = self.return_first_exist(t.xpath('coordinates/@precision'))
                    precision = None
                    gazetteer_entry = self.return_first_exist(t.xpath('gazetteer-entry/text()'))
                    gazetteer_ref_ref = self.return_first_exist(t.xpath('gazetteer-entry/@gazetteer-ref'))
                    gazetteer_ref = None
                    location_id_vocabulary_ref = self.return_first_exist(t.xpath('location-id/@vocabulary'))
                    location_id_vocabulary = None
                    location_id_code = self.return_first_exist(t.xpath('location-id/@code'))
                    adm_code = self.return_first_exist(t.xpath('administrative/@code'))
                    adm_vocabulary_ref = self.return_first_exist(t.xpath('administrative/@vocabulary'))
                    adm_vocabulary = None
                    adm_level = self.return_first_exist(t.xpath('administrative/@level'))
                    activity_description = self.return_first_exist(t.xpath('activity-description/text()'))
                    exactness_ref = self.return_first_exist(t.xpath('exactness/@code'))
                    exactness = None
                    location_reach_ref = self.return_first_exist(t.xpath('location-reach/@code'))
                    location_reach = None
                    location_class_ref = self.return_first_exist(t.xpath('location-class/@code'))
                    location_class = None
                    feature_designation_ref = self.return_first_exist(t.xpath('feature-designation/@code'))
                    feature_designation = None
                    point_srs_name = self.return_first_exist(t.xpath('point/@srsName'))
                    point_pos = self.return_first_exist(t.xpath('point/pos/text()'))


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

                    if location_reach_ref:
                        if models.GeographicLocationReach.objects.filter(code=location_reach_ref).exists():
                            location_reach = models.GeographicLocationReach.objects.get(code=location_reach_ref)

                    if location_id_vocabulary_ref:
                        if models.GeographicVocabulary.objects.filter(code=location_id_vocabulary_ref).exists():
                            location_id_vocabulary = models.GeographicVocabulary.objects.get(code=location_id_vocabulary_ref)



                    if adm_vocabulary_ref:
                        if models.GeographicVocabulary.objects.filter(code=adm_vocabulary_ref).exists():
                            adm_vocabulary = models.GeographicVocabulary.objects.get(code=adm_vocabulary_ref)

                    if exactness_ref:
                        if models.GeographicExactness.objects.filter(code=exactness_ref).exists():
                            exactness = models.GeographicExactness.objects.get(code=exactness_ref)

                    if location_class_ref:
                        if models.GeographicLocationClass.objects.filter(code=location_class_ref).exists():
                            location_class = models.GeographicLocationClass.objects.get(code=location_class_ref)

                    if feature_designation_ref:
                        if models.LocationType.objects.filter(code=feature_designation_ref).exists():
                            feature_designation = models.LocationType.objects.get(code=feature_designation_ref)

                    new_location = models.Location(activity=activity, ref=ref, name=name, type=type, type_description=type_description, description=description, description_type=description_type, adm_country_iso=adm_country_iso, adm_country_adm1=adm_country_adm1, adm_country_adm2=adm_country_adm2, adm_country_name=adm_country_name, percentage=percentage, latitude=latitude, longitude=longitude, precision=precision, gazetteer_entry=gazetteer_entry, gazetteer_ref=gazetteer_ref, location_reach=location_reach, location_id_vocabulary=location_id_vocabulary, location_id_code=location_id_code, adm_code=adm_code, adm_vocabulary=adm_vocabulary, adm_level=adm_level, activity_description=activity_description, exactness=exactness, location_class=location_class, feature_designation=feature_designation, point_srs_name=point_srs_name, point_pos=point_pos)
                    new_location.save()



                except Exception as e:
                    exception_handler(e, activity.id, "add_location")
        except Exception as e:
                exception_handler(e, activity.id, "add_location")

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



                except Exception as e:
                    exception_handler(e, activity.id, "add_conditions")
        except Exception as e:
            exception_handler(e, activity.id, "add_conditions")


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



                    document_link = models.DocumentLink(activity=activity, url=url, file_format=file_format, document_category=doc_category, title=title)
                    document_link.save()



                except Exception as e:
                    exception_handler(e, activity.id, "add_document_link")
        except Exception as e:
            exception_handler(e, activity.id, "add_document_link")




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


                except Exception as e:
                    exception_handler(e, activity.id, "add_country_budget_items")
        except Exception as e:
            exception_handler(e, activity.id, "add_country_budget_items")



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



                except Exception as e:
                    exception_handler(e, activity.id, "add_crs_add")
        except Exception as e:
            exception_handler(e, activity.id, "add_crs_add")



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


                except Exception as e:
                    exception_handler(e, activity.id, "add_fss")
        except Exception as e:
            exception_handler(e, activity.id, "add_fss")


    def add_total_budget(self, activity):

        try:
            updater = TotalBudgetUpdater()
            updater.update_single_activity(activity.id)
        except Exception as e:
            exception_handler(e, activity.id, "add_total_budget")

    def add_activity_search_data(self, activity):
        search_data = models.ActivitySearchData(activity = activity)

        search_data.search_identifier = activity.iati_identifier
        for title in activity.title_set.all():
            search_data.search_title = u'{orig_title} {add_title} '.format(
                orig_title=search_data.search_title or '',
                add_title=title.title or ''
            )

        for description in activity.description_set.all():
            search_data.search_title = u'{orig_description} {add_description} '.format(
                orig_description=search_data.search_description or '',
                add_description=description.description or ''
            )

        for country in activity.recipient_country.all():
            search_data.search_country_name = u'{orig_country_name} {add_country_name} '.format(
                orig_country_name=search_data.search_country_name or '',
                add_country_name=country.name or ''
            )

        for region in activity.recipient_region.all():
            search_data.search_region_name = u'{orig_region_name} {add_region_name} '.format(
                orig_region_name=search_data.search_region_name or '',
                add_region_name=region.name or ''
            )

        for sector in activity.sector.all():
            search_data.search_sector_name = u'{orig_sector_name} {add_sector_name} '.format(
                orig_sector_name=search_data.search_sector_name or '',
                add_sector_name=sector.name or ''
            )

        for organisation in activity.participating_organisations.all():
            search_data.search_participating_organisation_name = u'{orig_organisation_name} {add_organisation_name} '.format(
                orig_organisation_name=search_data.search_participating_organisation_name or '',
                add_organisation_name=organisation.name or ''
            )

        if not activity.reporting_organisation is None:
            search_data.search_reporting_organisation_name = u'{add_organisation_name}'.format(
                add_organisation_name=activity.reporting_organisation.name or ''
            )

        for document in activity.documentlink_set.all():
            search_data.search_documentlink_title = u'{orig_documentlink_title} {add_documentlink_title} '.format(
                orig_documentlink_title=search_data.search_documentlink_title or '',
                add_documentlink_title=document.title or ''
            )

        search_data.save()
