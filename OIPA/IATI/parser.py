from lxml import etree
import urllib2
import IATI.models as models
from re import sub
import httplib
from django.db import IntegrityError
from exceptions import TypeError
from django.core.exceptions import ValidationError
import time
from datetime import datetime
from deleter import Deleter
from lxml.etree import XMLSyntaxError

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
                context = etree.iterparse( iati_file, tag='iati-activity' )
                self.fast_iter(context, self.process_element)
                iati_file = None
                # gc.collect()
        except XMLSyntaxError, e:
            print "XMLSyntaxError" + e.message



    def get_the_file(self, url, try_number = 0):
        try:
            #get the file
            iati_file_url_object = urllib2.Request(url)
            file_opener = urllib2.build_opener()
            iati_file = file_opener.open(iati_file_url_object)
            return iati_file;

        except urllib2.HTTPError, e:
            print 'HTTPError (url=' + url + ') = ' + str(e.code)
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            print 'URLError (url=' + url + ') = ' + str(e.reason)
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except httplib.HTTPException, e:
            print 'HTTPException reading url ' + url
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except Exception as e:
                print '%s (%s)' % (e.message, type(e)) + " in get_the_file: " + url


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
            print '%s (%s)' % (e.message, type(e))


    def process_element(self, elem):

        if self.activity_exists(elem):
            self.remove_old_values_for_activity(elem)

        self.add_all_activity_data(elem)


    def add_all_activity_data(self, elem):

        try:

            # add basics
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
            self.add_conditions( elem, activity)

            # ManyToMany
            self.add_sectors(elem, activity)
            self.add_participating_organisations(elem, activity)
            self.add_countries(elem, activity)
            self.add_regions(elem, activity)
            self.add_policy_markers(elem, activity)
            self.add_activity_date(elem, activity)

        except Exception as e:
                print "error"
                print '%s (%s)' % (e.args[0], type(e))
                print " in add_all_activity_data: " + activity.id


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
                if len(unvalidated_date) == 4:
                    unvalidated_date = unvalidated_date + "-01-01"
                validated_date = time.strptime(unvalidated_date, '%Y-%m-%d')
                valid_date = datetime.fromtimestamp(time.mktime(validated_date))


            except ValueError:
                print('Invalid date!')
                print unvalidated_date
                valid_date = None
        return valid_date


    def activity_exists(self, elem):

        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
        activity_id = activity_id.replace(" ", "")

        if models.activity.objects.filter(id=activity_id).exists():
            return True
        else:
            return False

    def remove_old_values_for_activity(self, elem):
        deleter = Deleter()
        deleter.remove_old_values_for_activity(elem)


    def delete_all_activities_from_source(self, xml_source_ref):
        deleter = Deleter()
        deleter.delete_by_source(xml_source_ref)


    def exception_handler(self, e, ref, current_def):
        if e.args:
            print e.args[0]
        print " in " + current_def + ": " + ref

    # entity add functions
    def add_organisation(self, elem):
        ref = self.return_first_exist(elem.xpath( 'reporting-org/@ref' ))
        type_ref = self.return_first_exist(elem.xpath( 'reporting-org/@type' ))
        type = None
        name = self.return_first_exist(elem.xpath('reporting-org/text()'))
        if ref:
            try:
                if not models.organisation.objects.filter(code=ref).exists():


                    if not models.organisation_identifier.objects.filter(code=ref).exists():
                        abbreviation = None


                    else:
                        org_identifier = models.organisation_identifier.objects.get(code=ref)
                        abbreviation = org_identifier.abbreviation
                        name = org_identifier.name

                    if type_ref:
                        try:
                            isnumber = int(type_ref)
                            if models.organisation_type.objects.filter(code=type_ref).exists():
                                type = models.organisation_type.objects.get(code=type_ref)
                        except ValueError:
                            if models.organisation_type.objects.filter(name=type_ref).exists():
                                type = models.organisation_type.objects.get(name=type_ref)


                    new_organisation = models.organisation(code=ref, type=type, abbreviation=abbreviation, name=name)
                    new_organisation.save()

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
            activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
            activity_id = activity_id.strip(' \t\n\r')
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
            reporting_organisation_ref = self.return_first_exist(elem.xpath( 'reporting-org/@ref' ))
            reporting_organisation = None

            activity_status_code = self.return_first_exist(elem.xpath( 'activity-status/@code' ))
            activity_status_name = self.return_first_exist(elem.xpath( 'activity-status/text()' ))
            activity_status = None

            collaboration_type_ref = self.return_first_exist(elem.xpath( 'collaboration-type/@code' ))
            collaboration_type = None
            default_flow_type_ref = self.return_first_exist(elem.xpath( 'default-flow-type/@code' ))
            default_flow_type = None
            default_aid_type_ref = self.return_first_exist(elem.xpath( 'default-aid-type/@code' ))
            default_aid_type = None
            default_finance_type_ref = self.return_first_exist(elem.xpath( 'default-finance-type/@code' ))
            default_finance_type = None
            default_tied_status_ref = self.return_first_exist(elem.xpath( 'default-tied-status/@code' ))
            default_tied_status = None


            #get foreign key objects
            if default_currency_ref:
                if models.currency.objects.filter(code=default_currency_ref).exists():
                    default_currency = models.currency.objects.get(code=default_currency_ref)

            #activity status
            if activity_status_code and self.isInt(activity_status_code):
                if models.activity_status.objects.filter(code=activity_status_code).exists():
                    activity_status = models.activity_status.objects.get(code=activity_status_code)

            if reporting_organisation_ref:
                if models.organisation.objects.filter(code=reporting_organisation_ref).exists():
                    reporting_organisation = models.organisation.objects.get(code=reporting_organisation_ref)

            if collaboration_type_ref and self.isInt(collaboration_type_ref):
                if models.collaboration_type.objects.filter(code=collaboration_type_ref).exists():
                    collaboration_type = models.collaboration_type.objects.get(code=collaboration_type_ref)

            if default_flow_type_ref and self.isInt(default_flow_type_ref):
                if models.flow_type.objects.filter(code=default_flow_type_ref).exists():
                    default_flow_type = models.flow_type.objects.get(code=default_flow_type_ref)

            if default_aid_type_ref:
                if models.aid_type.objects.filter(code=default_aid_type_ref).exists():
                    default_aid_type = models.aid_type.objects.get(code=default_aid_type_ref)

            if default_finance_type_ref and self.isInt(default_finance_type_ref):
                if models.finance_type.objects.filter(code=default_finance_type_ref).exists():
                    default_finance_type = models.finance_type.objects.get(code=default_finance_type_ref)

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

                if models.tied_status.objects.filter(code=default_tied_status_ref).exists():
                    default_tied_status = models.tied_status.objects.get(code=default_tied_status_ref)

            if not self.isInt(hierarchy):
                hierarchy = None

            new_activity = models.activity(id=activity_id, default_currency=default_currency, hierarchy=hierarchy, last_updated_datetime=last_updated_datetime, linked_data_uri=linked_data_uri, reporting_organisation=reporting_organisation, activity_status=activity_status, collaboration_type=collaboration_type, default_flow_type=default_flow_type, default_aid_type=default_aid_type, default_finance_type=default_finance_type, default_tied_status=default_tied_status, xml_source_ref=self.xml_source_ref)
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

                    new_other_identifier = models.other_identifier(activity=activity, owner_ref=owner_ref, owner_name=owner_name, identifier=other_identifier)
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
                    language_ref = self.return_first_exist(t.xpath( '@xml:lang' ))
                    language = None

                    if language_ref:
                        if models.language.objects.filter(code=language_ref).exists():
                            language = models.language.objects.get(code=language_ref)

                    new_title = models.title(activity=activity, title=title, language=language)
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


                    if language_ref:
                        if models.language.objects.filter(code=language_ref).exists():
                            language = models.language.objects.get(code=language_ref)

                    if type_ref:
                        try:
                            if models.description_type.objects.filter(code=type_ref).exists():
                                type = models.description_type.objects.get(code=type_ref)
                        except ValueError:
                            # nasty exception to make wrong use of type ref right
                            if not description:
                                description = type_ref


                    new_description = models.description(activity=activity, description=description, type=type, language=language)
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
                        if models.budget_type.objects.filter(code=type_ref).exists():
                            type = models.budget_type.objects.get(code=type_ref)

                    if currency_ref:
                        if models.currency.objects.filter(code=currency_ref).exists():
                            currency = models.currency.objects.get(code=currency_ref)

                    new_budget = models.budget(activity=activity, type=type, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency)
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
                        if models.currency.objects.filter(code=currency_ref).exists():
                            currency = models.currency.objects.get(code=currency_ref)

                    new_planned_disbursement = models.planned_disbursement(activity=activity, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency, updated=updated)
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

                    new_website = models.activity_website(activity=activity, url=url)
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

                    new_contact = models.contact_info(activity=activity, person_name=person_name, organisation=organisation, telephone=telephone, email=email, mailing_address=mailing_address)
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
                    provider_activity = self.return_first_exist(t.xpath('provider-org/@provider-activity-id'))
                    receiver_organisation_ref = self.return_first_exist(t.xpath('receiver-org/@ref'))
                    receiver_organisation = None
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
                        if models.aid_type.objects.filter(code=aid_type_ref).exists():
                            aid_type = models.aid_type.objects.get(code=aid_type_ref)
                    else:
                        aid_type = activity.default_aid_type

                    if description_type_ref:
                        if models.description_type.objects.filter(code=description_type_ref).exists():
                            description_type = models.description_type.objects.get(code=description_type_ref)

                    if disbursement_channel_ref:
                        if models.disbursement_channel.objects.filter(code=disbursement_channel_ref).exists():
                            disbursement_channel = models.disbursement_channel.objects.get(code=disbursement_channel_ref)

                    if finance_type_ref:
                        if models.finance_type.objects.filter(code=finance_type_ref).exists():
                            finance_type = models.finance_type.objects.get(code=finance_type_ref)
                    else:
                        finance_type = activity.default_finance_type

                    if flow_type_ref:
                        if models.flow_type.objects.filter(code=flow_type_ref).exists():
                            flow_type = models.flow_type.objects.get(code=flow_type_ref)
                    else:
                        flow_type = activity.default_flow_type

                    if provider_organisation_ref:
                        if models.organisation.objects.filter(code=provider_organisation_ref).exists():
                            provider_organisation = models.organisation.objects.get(code=provider_organisation_ref)
                        else:
                            provider_organisation_name_ref = self.return_first_exist(t.xpath('provider-org/text()'))

                            if models.organisation.objects.filter(name=provider_organisation_name_ref).exists():
                                provider_organisation = models.organisation.objects.get(name=provider_organisation_name_ref)
                            else:
                                provider_organisation_type = None
                                provider_organisation_type_ref = self.return_first_exist(t.xpath('provider-org/@type'))
                                if provider_organisation_type_ref:
                                    if models.organisation_type.objects.filter(code=provider_organisation_type_ref).exists():
                                        provider_organisation_type = models.organisation_type.objects.get(code=provider_organisation_type_ref)


                                try:

                                    new_organisation = models.organisation(code=provider_organisation_ref, abbreviation=None, type=provider_organisation_type, reported_by_organisation=None, name=provider_organisation_name_ref)
                                    new_organisation.save()

                                except Exception as e:
                                    print '%s (%s)' % (e.message, type(e)) + " in add_transaction during adding provider organisation: " + activity.id


                    if receiver_organisation_ref:
                        if models.organisation.objects.filter(code=receiver_organisation_ref).exists():
                            receiver_organisation = models.organisation.objects.get(code=receiver_organisation_ref)
                        else:
                            receiver_organisation_name_ref = self.return_first_exist(t.xpath('receiver-org/text()'))

                            if models.organisation.objects.filter(name=receiver_organisation_name_ref).exists():
                                receiver_organisation = models.organisation.objects.get(name=receiver_organisation_name_ref)
                            else:

                                receiver_organisation_type = None
                                receiver_organisation_type_ref = self.return_first_exist(t.xpath('receiver-org/@type'))
                                if receiver_organisation_type_ref:
                                    if models.organisation_type.objects.filter(code=receiver_organisation_type_ref).exists():
                                        receiver_organisation_type = models.organisation_type.objects.get(code=receiver_organisation_type_ref)


                                try:

                                    new_organisation = models.organisation(code=receiver_organisation_ref, abbreviation=None, type=receiver_organisation_type, reported_by_organisation=None, name=receiver_organisation_name_ref)
                                    new_organisation.save()

                                except Exception as e:
                                    print '%s (%s)' % (e.message, type(e)) + " in add_transaction during adding receiver organisation: " + activity.id


                    if tied_status_ref:
                        if models.tied_status.objects.filter(code=tied_status_ref).exists():
                            tied_status = models.tied_status.objects.get(code=tied_status_ref)
                    else:
                        tied_status = activity.default_tied_status

                    if transaction_type_ref:
                        if models.transaction_type.objects.filter(code=transaction_type_ref).exists():
                            transaction_type = models.transaction_type.objects.get(code=transaction_type_ref)

                    if currency_ref:
                        if models.currency.objects.filter(code=currency_ref).exists():
                            currency = models.currency.objects.get(code=currency_ref)
                    else:
                        currency = activity.default_currency


                    new_transaction = models.transaction(activity=activity, aid_type=aid_type, description=description, description_type=description_type, disbursement_channel=disbursement_channel, finance_type=finance_type, flow_type=flow_type, provider_organisation=provider_organisation, provider_activity=provider_activity, receiver_organisation=receiver_organisation, tied_status=tied_status, transaction_date=transaction_date, transaction_type=transaction_type, value_date=value_date, value=value, ref=ref, currency=currency)
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
                    description = self.return_first_exist(t.xpath('description/text()'))

                    if type_ref:
                        type_ref = type_ref.lower()
                        if type_ref == 'output':
                            type_ref = '1'
                        if type_ref == 'outcome':
                            type_ref = '2'
                        if type_ref == 'impact':
                            type_ref == '3'
                        if models.result_type.objects.filter(code=type_ref).exists():
                            type = models.result_type.objects.get(code=type_ref)


                    new_result = models.result(activity=activity, result_type=type, title=title, description=description)
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
                        if models.sector.objects.filter(code=sector_code).exists():
                            sector = models.sector.objects.get(code=sector_code)

                    if not sector:
                        sector_name = self.return_first_exist(t.xpath( 'text()' ))
                        if models.sector.objects.filter(name=sector_name).exists():
                            sector = models.sector.objects.get(name=sector_name)

                    if vocabulary_code:
                        if models.vocabulary.objects.filter(code=vocabulary_code).exists():
                            vocabulary = models.vocabulary.objects.get(code=vocabulary_code)

                    if not sector:
                        alt_sector_name = sector_code
                    else:
                        alt_sector_name = None

                    new_activity_sector = models.activity_sector(activity=activity, sector=sector,alt_sector_name=alt_sector_name, vocabulary=vocabulary, percentage = percentage)
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
                        if models.country.objects.filter(code=country_ref).exists():
                            country = models.country.objects.get(code=country_ref)
                        else:
                            country_ref = country_ref.upper()
                            if models.country.objects.filter(name=country_ref).exists():
                                country = models.country.objects.get(name=country_ref)
                    else:
                        continue

                    new_activity_country = models.activity_recipient_country(activity=activity, country=country, percentage = percentage)
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

                region_ref = self.return_first_exist(t.xpath( '@code' ))
                region = None
                percentage = self.return_first_exist(t.xpath('@percentage'))
                if percentage:
                        percentage = percentage.replace("%", "")

                if region_ref:
                    if models.region.objects.filter(code=region_ref).exists():
                        region = models.region.objects.get(code=region_ref)
                    elif models.region.objects.filter(name=region_ref).exists():
                            region = models.region.objects.get(name=region_ref)
                    else:
                        print "error in add regions, unknown region: " + region_ref
                else:
                    continue

                try:
                    new_activity_region = models.activity_recipient_region(activity=activity, region=region, percentage = percentage)
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

                    if participating_organisation_ref:
                        if models.organisation.objects.filter(code=participating_organisation_ref).exists():
                            participating_organisation = models.organisation.objects.get(code=participating_organisation_ref)
                        else:
                            new_po = models.organisation(code=participating_organisation_ref)
                            new_po.save()
                            participating_organisation = new_po

                    if role_ref:
                        if models.organisation_role.objects.filter(code=role_ref).exists():
                            role = models.organisation_role.objects.get(code=role_ref)


                    new_activity_participating_organisation = models.activity_participating_organisation(activity=activity, organisation=participating_organisation, role=role, name=name)
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
                        if models.policy_marker.objects.filter(code=policy_marker_code).exists():
                            policy_marker = models.policy_marker.objects.get(code=policy_marker_code)
                    else:
                        policy_marker_name = self.return_first_exist(t.xpath( 'text()' ))
                        if policy_marker_name:
                            if models.policy_marker.objects.filter(name=policy_marker_name).exists():
                                policy_marker = models.policy_marker.objects.get(code=policy_marker_name)

                    if policy_marker_voc:
                        if models.vocabulary.objects.filter(code=policy_marker_voc).exists():
                            vocabulary = models.vocabulary.objects.get(code=policy_marker_voc)

                    if policy_marker_significance:
                        if models.policy_significance.objects.filter(code=policy_marker_significance).exists():
                            significance = models.policy_significance.objects.get(code=policy_marker_significance)


                    new_activity_policy_marker = models.activity_policy_marker(activity=activity, policy_marker=policy_marker, vocabulary=vocabulary, policy_significance=significance)
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
                        if models.activity_date_type.objects.filter(code=type_ref).exists():
                            type = models.activity_date_type.objects.get(code=type_ref)
                        else:
                            type_ref = type_ref.lower();
                            type_ref = type_ref.replace(' ', '-');

                            if models.activity_date_type.objects.filter(code=type_ref).exists():
                                type = models.activity_date_type.objects.get(code=type_ref)


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
                        if models.related_activity_type.objects.filter(code=type_ref).exists():
                            type = models.related_activity_type.objects.get(code=type_ref)

                    new_related_activity = models.related_activity(current_activity=activity, type=type, ref=ref, text=text)
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
                        if models.location_type.objects.filter(code=type_ref).exists():
                            type = models.location_type.objects.get(code=type_ref)

                    if description_type_ref:
                        if models.description_type.objects.filter(code=description_type_ref).exists():
                            description_type = models.description_type.objects.get(code=description_type_ref)

                    if adm_country_iso_ref:
                        if models.country.objects.filter(code=adm_country_iso_ref).exists():
                            adm_country_iso = models.country.objects.get(code=adm_country_iso_ref)

                    if precision_ref:
                        if models.geographical_precision.objects.filter(code=precision_ref).exists():
                            precision = models.geographical_precision.objects.get(code=precision_ref)

                    if gazetteer_ref_ref:
                        if models.gazetteer_agency.objects.filter(code=gazetteer_ref_ref).exists():
                            gazetteer_ref = models.gazetteer_agency.objects.get(code=gazetteer_ref_ref)


                    new_location = models.location(activity=activity, name=name, type=type, type_description=type_description, description=description, description_type=description_type, adm_country_iso=adm_country_iso, adm_country_adm1=adm_country_adm1, adm_country_adm2=adm_country_adm2, adm_country_name=adm_country_name, percentage=percentage, latitude=latitude, longitude=longitude, precision=precision, gazetteer_entry=gazetteer_entry, gazetteer_ref=gazetteer_ref)
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
            for t in elem.xpath('location/conditions/condition'):

                try:
                    condition_type_ref = self.return_first_exist(t.xpath('@type'))
                    condition_type = None
                    condition = self.return_first_exist(t.xpath('text()'))

                    if condition_type_ref:
                        if models.condition_type.objects.filter(code=condition_type_ref).exists():
                            condition_type = models.condition_type.objects.get(code=condition_type_ref)

                    new_condition = models.condition(activity=activity, text=condition, type=condition_type)
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


