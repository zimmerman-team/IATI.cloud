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
from geodata.models import country, region
import gc

class Parser():

    def parse_url(self, url, xml_source_ref):

        def fast_iter(context, func):
            for event, elem in context:
                try:
                    func(self, elem)
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e))
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
            del context

        def process_element(self, elem):

            if activity_exists(self, elem):
                if needs_update(self, elem):
                    remove_old_values_for_activity(self, elem)
                    add_all_activity_data(self, elem)
            #   else do nothing
            else:
                add_all_activity_data(self, elem)


        def add_all_activity_data(self, elem):

            try:

                # add basics
                add_organisation(self, elem)
                activity = add_activity(self, elem)
                add_other_identifier(self, elem, activity)
                add_activity_title(self, elem, activity)
                add_activity_description(self, elem, activity)
                add_budget(self, elem, activity)
                add_planned_disbursement(self, elem, activity)
                add_website(self, elem, activity)
                add_contact_info(self, elem, activity)
                add_transaction(self, elem, activity)
                add_result(self, elem, activity)
                add_location(self, elem, activity)
                add_related_activities(self, elem, activity)
                add_conditions(self, elem, activity)

                # ManyToMany
                add_sectors(self, elem, activity)
                add_participating_organisations(self, elem, activity)
                add_countries(self, elem, activity)
                add_regions(self, elem, activity)
                add_policy_markers(self, elem, activity)
                add_activity_date(self, elem, activity)


            except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in process_element: " + activity.id




        # class wide functions
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

        def validate_date(unvalidated_date):
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
                    valid_date = None
            return valid_date


        def activity_exists(self, elem):

            activity_id = return_first_exist(elem.xpath( 'iati-identifier/text()' ))
            activity_id = activity_id.replace(" ", "")

            if models.activity.objects.filter(id=activity_id).exists():
                return True
            else:
                return False


        def needs_update(self, elem):

            activity_id = return_first_exist(elem.xpath( 'iati-identifier/text()' ))
            activity_id = activity_id.replace(" ", "")

            cur_activity = models.activity.objects.get(id=activity_id)
            last_updated_datetime = cur_activity.last_updated_datetime

            if last_updated_datetime == return_first_exist(elem.xpath('@last-updated-datetime')) and last_updated_datetime:
                return False
            else:
                return True


        def remove_old_values_for_activity(self, elem):

            activity_id = return_first_exist(elem.xpath( 'iati-identifier/text()' ))
            activity_id = activity_id.replace(" ", "")

            cur_activity = models.activity.objects.get(id=activity_id)

            models.activity_recipient_country.objects.filter(activity=cur_activity).delete()
            models.activity_sector.objects.filter(activity=cur_activity).delete()
            models.activity_date.objects.filter(activity=cur_activity).delete()
            models.activity_website.objects.filter(activity=cur_activity).delete()
            models.activity_participating_organisation.objects.filter(activity=cur_activity).delete()
            models.activity_policy_marker.objects.filter(activity=cur_activity).delete()
            models.activity_recipient_region.objects.filter(activity=cur_activity).delete()
            models.related_activity.objects.filter(current_activity=cur_activity).delete()
            models.other_identifier.objects.filter(activity=cur_activity).delete()
            models.title.objects.filter(activity=cur_activity).delete()
            models.description.objects.filter(activity=cur_activity).delete()
            models.contact_info.objects.filter(activity=cur_activity).delete()
            models.location.objects.filter(activity=cur_activity).delete()
            models.transaction.objects.filter(activity=cur_activity).delete()
            models.budget.objects.filter(activity=cur_activity).delete()
            models.planned_disbursement.objects.filter(activity=cur_activity).delete()
            models.condition.objects.filter(activity=cur_activity).delete()
            models.result.objects.filter(activity=cur_activity).delete()
            models.document_link.objects.filter(activity=cur_activity).delete()
            cur_activity.delete()


        # entity add functions
        def add_organisation(self, elem):
            ref = return_first_exist(elem.xpath( 'reporting-org/@ref' ))
            type_ref = return_first_exist(elem.xpath( 'reporting-org/@type' ))
            type = None
            name = return_first_exist(elem.xpath('reporting-org/text()'))
            if ref:
                try:
                    if not models.organisation.objects.filter(code=ref).exists():


                        if not models.organisation_identifier.objects.filter(code=ref).exists():
                            abbreviation = None

                            # new_organisation_identifier = models.organisation_identifier(code=ref, abbreviation="", name="")
                            # new_organisation_identifier.save()
                            # org_identifier = new_organisation_identifier
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
                    print e.message + " in add_organisation: "+ ref
                    
                except TypeError, e:
                    print e.message + " in add_organidation: "+ ref
                    
                except ValidationError, e:
                    print e.message + " in add_organisation: "+ ref
                    
                except IntegrityError, e:
                    print e.message + " in add_organisation: "+ ref
                except Exception as e:
                    print "error in add_organisation(elem) " + ref
                    print '%s (%s)' % (e.message, type(e))
                    print e.messages



        def add_activity(self, elem):
            try:
                activity_id = return_first_exist(elem.xpath( 'iati-identifier/text()' ))
                activity_id = activity_id.replace(" ", "")
                default_currency_ref = return_first_exist(elem.xpath('@default-currency'))
                default_currency = None

                hierarchy = return_first_exist(elem.xpath('@hierarchy'))
                last_updated_datetime = return_first_exist(elem.xpath('@last-updated-datetime'))
                # if last_updated_datetime:
                #     last_updated_datetime = last_updated_datetime.split('+')[0]
                #     last_updated_datetime = last_updated_datetime.split('-')[0]
                # strp_time = time.strptime(last_updated_datetime_str, '%Y-%m-%d %H:%M:%S')
                # last_updated_datetime = datetime.fromtimestamp(time.mktime(strp_time))



                linked_data_uri = return_first_exist(elem.xpath('@linked-data-uri'))
                reporting_organisation_ref = return_first_exist(elem.xpath( 'reporting-org/@ref' ))
                reporting_organisation = None

                activity_status_code = return_first_exist(elem.xpath( 'activity-status/@code' ))
                activity_status_name = return_first_exist(elem.xpath( 'activity-status/text()' ))
                activity_status = None

                collaboration_type_ref = return_first_exist(elem.xpath( 'collaboration-type/@code' ))
                collaboration_type = None
                default_flow_type_ref = return_first_exist(elem.xpath( 'default-flow-type/@code' ))
                default_flow_type = None
                default_aid_type_ref = return_first_exist(elem.xpath( 'default-aid-type/@code' ))
                default_aid_type = None
                default_finance_type_ref = return_first_exist(elem.xpath( 'default-finance-type/@code' ))
                default_finance_type = None
                default_tied_status_ref = return_first_exist(elem.xpath( 'default-tied-status/@code' ))
                default_tied_status = None


                #get foreign key objects
                if default_currency_ref:
                    if models.currency.objects.filter(code=default_currency_ref).exists():
                        default_currency = models.currency.objects.get(code=default_currency_ref)

                #activity status
                if activity_status_code:
                    if models.activity_status.objects.filter(code=activity_status_code).exists():
                        activity_status = models.activity_status.objects.get(code=activity_status_code)

                if reporting_organisation_ref:
                    if models.organisation.objects.filter(code=reporting_organisation_ref).exists():
                        reporting_organisation = models.organisation.objects.get(code=reporting_organisation_ref)

                if collaboration_type_ref:
                    if models.collaboration_type.objects.filter(code=collaboration_type_ref).exists():
                        collaboration_type = models.collaboration_type.objects.get(code=collaboration_type_ref)

                if default_flow_type_ref:
                    if models.flow_type.objects.filter(code=default_flow_type_ref).exists():
                        default_flow_type = models.flow_type.objects.get(code=default_flow_type_ref)

                if default_aid_type_ref:
                    if models.aid_type.objects.filter(code=default_aid_type_ref).exists():
                        default_aid_type = models.aid_type.objects.get(code=default_aid_type_ref)

                if default_finance_type_ref:
                    if models.finance_type.objects.filter(code=default_finance_type_ref).exists():
                        default_finance_type = models.finance_type.objects.get(code=default_finance_type_ref)

                if default_tied_status_ref:
                    default_tied_status_ref = default_tied_status_ref.lower()
                    if default_tied_status_ref == "partially tied":
                        default_tied_status_ref = "3"
                    if default_tied_status_ref == "tied":
                        default_tied_status_ref = "4"
                    if default_tied_status_ref == "untied":
                        default_tied_status_ref = "5"

                    if models.tied_status.objects.filter(code=default_tied_status_ref).exists():
                        default_tied_status = models.tied_status.objects.get(code=default_tied_status_ref)

                try:
                    int(hierarchy)
                except ValueError:
                    hierarchy = None
                except TypeError:
                    hierarchy = None


                new_activity = models.activity(id=activity_id, default_currency=default_currency, hierarchy=hierarchy, last_updated_datetime=last_updated_datetime, linked_data_uri=linked_data_uri, reporting_organisation=reporting_organisation, activity_status=activity_status, collaboration_type=collaboration_type, default_flow_type=default_flow_type, default_aid_type=default_aid_type, default_finance_type=default_finance_type, default_tied_status=default_tied_status, xml_source_ref=xml_source_ref)
                new_activity.save()

                return new_activity

            except IntegrityError, e:
                print e.message + " in add_activity: " + activity_id
                
            except ValueError, e:
                print e.message + " in add_activity: "+ activity_id
                
            except ValidationError, e:
                    print e.message + " in add_activity: "+ activity_id
            except TypeError, e:
                    print e.message + " in add_activity: "+ activity_id
            except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_activity: " + activity_id




        #after activity is added

        # add one to many
        def add_other_identifier(self, elem, activity):

            for t in elem.xpath('other-identifier'):

                try:
                    owner_ref = return_first_exist(t.xpath( '@owner-ref' ))
                    owner_name = return_first_exist(t.xpath( '@owner-name' ))
                    other_identifier = return_first_exist(t.xpath( 'text()' ))

                    new_other_identifier = models.other_identifier(activity=activity, owner_ref=owner_ref, owner_name=owner_name, identifier=other_identifier)
                    new_other_identifier.save()

                except IntegrityError, e:
                    print e.message + " in add_other_identifier: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_other_identifier: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_other_identifier: " + activity.id



        def add_activity_title(self, elem, activity):

            for t in elem.xpath('title'):
                try:
                    title = return_first_exist(t.xpath( 'text()' ))
                    language_ref = return_first_exist(t.xpath( '@xml:lang' ))
                    language = None

                    if language_ref:
                        if models.language.objects.filter(code=language_ref).exists():
                            language = models.language.objects.get(code=language_ref)

                        new_title = models.title(activity=activity, title=title, language=language)
                        new_title.save()

                except IntegrityError, e:
                    print e.message + " in add_title: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_title: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_title: " + activity.id



        def add_activity_description(self, elem, activity):

            for t in elem.xpath('description'):
                try:
                    description = return_first_exist(t.xpath( 'text()' ))
                    type_ref = return_first_exist(t.xpath('@type'))
                    type = None
                    language_ref = return_first_exist(t.xpath( '@xml:lang' ))
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
                    print e.message + " in add_description: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_description: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_description: " + activity.id


        def add_budget(self, elem, activity):

            for t in elem.xpath('budget'):

                try:
                    type_ref = return_first_exist(t.xpath( '@type' ))
                    type = None

                    period_start = return_first_exist(t.xpath( 'period-start/@iso-date'))
                    if not period_start:
                        period_start = return_first_exist(t.xpath('period-start/text()'))
                    period_end = return_first_exist(t.xpath( 'period-end/@iso-date'))
                    if not period_end:
                        period_end = return_first_exist(t.xpath('period-end/text()'))

                    value = return_first_exist(t.xpath( 'value/text()' ))
                    value_date = validate_date(return_first_exist(t.xpath('value/@value-date')))

                    currency_ref = return_first_exist(t.xpath('value/@currency'))
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
                    print e.message + " in add_budget: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_budget: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_budget: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_budget: " + activity.id



        def add_planned_disbursement(self, elem, activity):


            for t in elem.xpath('planned-disbursement'):

                try:
                    period_start = return_first_exist(t.xpath( 'period_start/@iso-date'))
                    if not period_start:
                        period_start = return_first_exist(t.xpath('period_start/text()'))
                    period_end = return_first_exist(t.xpath( 'period_end/@iso-date'))
                    if not period_end:
                        period_end = return_first_exist(t.xpath('period_end/text()'))

                    value = return_first_exist(t.xpath( 'value/text()' ))
                    value_date = return_first_exist(t.xpath('value/@value-date'))
                    currency_ref = return_first_exist(t.xpath('value/@currency'))
                    currency = None

                    updated = return_first_exist(t.xpath('@updated'))

                    if currency_ref:
                        if models.currency.objects.filter(code=currency_ref).exists():
                            currency = models.currency.objects.get(code=currency_ref)

                    new_planned_disbursement = models.planned_disbursement(activity=activity, period_start=period_start, period_end=period_end, value=value, value_date=value_date, currency=currency, updated=updated)
                    new_planned_disbursement.save()


                except IntegrityError, e:
                    print e.message + " in add_planned_disbursement: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_planned_disbursement: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_planned_disbursement: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_planned_disbursement: " + activity.id


        # add many to 1
        def add_website(self, elem, activity):

            for t in elem.xpath('activity-website'):
                try:

                    url = return_first_exist(t.xpath( 'text()'))

                    new_website = models.activity_website(activity=activity, url=url)
                    new_website.save()


                except IntegrityError, e:
                    print e.message + " in add_website: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_website: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_website: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_website: " + activity.id


        def add_contact_info(self, elem, activity):


            for t in elem.xpath('contact-info'):

                try:
                    person_name = return_first_exist(t.xpath('person-name/text()'))
                    organisation = return_first_exist(t.xpath('organisation/text()'))
                    telephone = return_first_exist(t.xpath('telephone/text()'))
                    email = return_first_exist(t.xpath('email/text()'))
                    mailing_address = return_first_exist(t.xpath('mailing-address/text()'))

                    new_contact = models.contact_info(activity=activity, person_name=person_name, organisation=organisation, telephone=telephone, email=email, mailing_address=mailing_address)
                    new_contact.save()

                except IntegrityError, e:
                    print e.message + " in add_contact_info: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_contact_info: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_contact_info: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_contact_info: " + activity.id


        def add_transaction(self, elem, activity):

            for t in elem.xpath('transaction'):

                try:

                    ref = return_first_exist(t.xpath('@ref'))
                    aid_type_ref = return_first_exist(t.xpath('aid-type/@code'))
                    aid_type = None
                    description = return_first_exist(t.xpath('description/text()'))

                    description_type_ref = return_first_exist(t.xpath('description/@type'))
                    description_type = None
                    disbursement_channel_ref = return_first_exist(t.xpath('disbursement-channel/@code'))
                    disbursement_channel = None
                    finance_type_ref = return_first_exist(t.xpath('finance-type/@code'))
                    finance_type = None
                    flow_type_ref = return_first_exist(t.xpath('flow-type/@code'))
                    flow_type = None
                    provider_organisation_ref = return_first_exist(t.xpath('provider-org/@ref'))
                    provider_organisation = None
                    provider_activity = return_first_exist(t.xpath('provider-org/@provider-activity-id'))
                    receiver_organisation_ref = return_first_exist(t.xpath('receiver-org/@ref'))
                    receiver_organisation = None
                    tied_status_ref = return_first_exist(t.xpath('tied-status/@code'))
                    tied_status = None
                    transaction_date = validate_date(return_first_exist(t.xpath('transaction-date/@iso-date')))

                    transaction_type_ref = return_first_exist(t.xpath('transaction-type/@code'))
                    transaction_type = None
                    value = return_first_exist(t.xpath('value/text()'))

                    if value:
                        value = value.replace(",", "")

                    value_date = validate_date(return_first_exist(t.xpath('value/@value-date')))

                    currency_ref = return_first_exist(t.xpath('value/@currency'))
                    currency = None

                    if aid_type_ref:
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

                    if receiver_organisation_ref:
                        if models.organisation.objects.filter(code=receiver_organisation_ref).exists():
                            receiver_organisation = models.organisation.objects.get(code=receiver_organisation_ref)

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
                    print e.message + " in add_transaction: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_transaction: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_transaction: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_transaction: " + activity.id



        def add_result(self, elem, activity):


            for t in elem.xpath('result'):
                try:
                    type_ref = return_first_exist(t.xpath('@type'))
                    type = None
                    title = return_first_exist(t.xpath('title/text()'))
                    description = return_first_exist(t.xpath('description/text()'))

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
                    print e.message + " in add_result: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_result: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_result: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_result: " + activity.id



        # add many to many relationship
        def add_sectors(self, elem, activity):

            for t in elem.xpath('sector'):
                try:
                    sector_code = return_first_exist(t.xpath( '@code' ))
                    sector = None
                    vocabulary_code = return_first_exist(t.xpath('@vocabulary'))
                    vocabulary = None
                    percentage = return_first_exist(t.xpath('@percentage'))
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
                        sector_name = return_first_exist(t.xpath( 'text()' ))
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
                    print e.message + "for activity: " + activity.id
                    print  "in add_sectors: " + sector_code
                except ValueError, e:
                    print e.message + "for activity: " + activity.id
                    print  "in add_sectors: " + sector_code
                except ValidationError, e:
                    print e.message + "for activity: " + activity.id
                    print  "in add_sectors: " + sector_code
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " for activity: " + activity.id
                    print "in add_sectors: " + sector_code




        def add_countries(self, elem, activity):

            for t in elem.xpath('recipient-country'):
                try:
                    country_ref = return_first_exist(t.xpath( '@code' ))
                    country = None
                    percentage = return_first_exist(t.xpath('@percentage'))
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
                    print e.message + " in add_countries: " + activity.id
                except ValueError, e:
                    print e.message + " in add_countries: " + activity.id
                except ValidationError, e:
                    print e.message + " in add_countries: " + activity.id
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_countries: " + activity.id

        
        def add_regions(self, elem, activity):

            for t in elem.xpath('recipient-region'):

                region_ref = return_first_exist(t.xpath( '@code' ))
                region = None
                percentage = return_first_exist(t.xpath('@percentage'))
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
                    print e.message + " in add_regions: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_regions: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_regions: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_regions: " + activity.id


        def add_participating_organisations(self, elem, activity):

            for t in elem.xpath('participating-org'):

                try:
                    participating_organisation_ref = return_first_exist(t.xpath( '@ref' ))
                    participating_organisation = None

                    name = return_first_exist(t.xpath( 'text()' ))

                    role_ref = return_first_exist(t.xpath('@role'))
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
                    print e.message + " in add_participating_organisations: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_participating_organisations: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_participating_organisations: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_participating_organisations: " + activity.id


        def add_policy_markers(self, elem, activity):

            for t in elem.xpath('policy-marker'):
                try:
                    policy_marker_code = return_first_exist(t.xpath( '@code' ))
                    alt_policy_marker = None
                    policy_marker = None
                    policy_marker_voc = return_first_exist(t.xpath( '@vocabulary' ))
                    vocabulary = None
                    policy_marker_significance = return_first_exist(t.xpath( '@significance' ))
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
                        policy_marker_name = return_first_exist(t.xpath( 'text()' ))
                        if policy_marker_name:
                            if models.policy_marker.objects.filter(name=policy_marker_name).exists():
                                policy_marker = models.policy_marker.objects.get(code=policy_marker_name)

                    if policy_marker_voc:
                        if models.vocabulary.objects.filter(code=vocabulary).exists():
                            vocabulary = models.vocabulary.objects.get(code=vocabulary)

                    if policy_marker_significance:
                        if models.policy_significance.objects.filter(code=policy_marker_significance).exists():
                            significance = models.policy_significance.objects.get(code=policy_marker_significance)


                    new_activity_policy_marker = models.activity_policy_marker(activity=activity, policy_marker=policy_marker, vocabulary=vocabulary, policy_significance=significance)
                    new_activity_policy_marker.save()

                except IntegrityError, e:
                    print e.message + " in add_policy_markers: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_policy_markers: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_policy_markers: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_policy_markers: " + activity.id




        def add_activity_date(self, elem, activity):

            for t in elem.xpath('activity-date'):

                try:
                    type_ref = return_first_exist(t.xpath( '@type' ))
                    type = None
                    curdate = return_first_exist(t.xpath( 'text()' ))

                    if not curdate:
                        curdate = return_first_exist(t.xpath( '@iso-date' ))

                    curdate = validate_date(curdate)



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
                    print e.message + " in add_activity_date: " + activity.id
                    
                except ValueError, e:
                    print e.message + " in add_activity_date: " + activity.id
                    
                except ValidationError, e:
                    print e.message + " in add_activity_date: " + activity.id
                    
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_activity_date: " + activity.id


        def add_related_activities(self, elem, activity):

            for t in elem.xpath('related-activity'):

                try:
                    type_ref = return_first_exist(t.xpath( '@type' ))
                    type = None
                    ref = return_first_exist(t.xpath('@ref'))
                    text = return_first_exist(t.xpath('text()'))

                    if type_ref:
                        if models.related_activity_type.objects.filter(code=type_ref).exists():
                            type = models.related_activity_type.objects.get(code=type_ref)

                    new_related_activity = models.related_activity(current_activity=activity, type=type, ref=ref, text=text)
                    new_related_activity.save()


                except IntegrityError, e:
                    print e.message + " in add_related_activities: " + activity.id

                except ValueError, e:
                    print e.message + " in add_related_activities: " + activity.id

                except ValidationError, e:
                    print e.message + " in add_related_activities: " + activity.id

                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_related_activities: " + activity.id




        def add_location(self, elem, activity):

            for t in elem.xpath('location'):

                try:
                    name = return_first_exist(t.xpath('name/text()'))
                    type_ref = return_first_exist(t.xpath('location-type/@code'))
                    type = None
                    type_description = return_first_exist(t.xpath('location-type/text()'))
                    description = return_first_exist(t.xpath('description/text()'))
                    description_type_ref = return_first_exist(t.xpath('description/@type'))
                    description_type = None
                    adm_country_iso_ref = return_first_exist(t.xpath('administrative/@country'))
                    adm_country_iso = None
                    adm_country_adm1 = return_first_exist(t.xpath('administrative/@adm1'))
                    adm_country_adm2 = return_first_exist(t.xpath('administrative/@adm2'))
                    adm_country_name = return_first_exist(t.xpath('administrative/text()'))
                    percentage = return_first_exist(t.xpath('@percentage'))
                    latitude = return_first_exist(t.xpath('coordinates/@latitude'))
                    longitude = return_first_exist(t.xpath('coordinates/@longitude'))
                    precision_ref = return_first_exist(t.xpath('coordinates/@precision'))
                    precision = None
                    gazetteer_entry = return_first_exist(t.xpath('gazetteer-entry/text()'))
                    gazetteer_ref_ref = return_first_exist(t.xpath('gazetteer-entry/@gazetteer-ref'))
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
                    print e.message + " in add_location: " + activity.id

                except ValueError, e:
                    print e.message + " in add_location: " + activity.id

                except ValidationError, e:
                    print e.message + " in add_location: " + activity.id

                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_location: " + activity.id


        def add_conditions(self, elem, activity):


            for t in elem.xpath('location/conditions/condition'):

                try:
                    condition_type_ref = return_first_exist(t.xpath('@type'))
                    condition_type = None
                    condition = return_first_exist(t.xpath('text()'))

                    if condition_type_ref:
                        if models.condition_type.objects.filter(code=condition_type_ref).exists():
                            condition_type = models.condition_type.objects.get(code=condition_type_ref)

                    new_condition = models.condition(activity=activity, text=condition, type=condition_type)
                    new_condition.save()


                except IntegrityError, e:
                    print e.message + " in add_conditions: " + activity.id

                except ValueError, e:
                    print e.message + " in add_conditions: " + activity.id

                except ValidationError, e:
                    print e.message + " in add_conditions: " + activity.id

                except Exception as e:
                    print '%s (%s)' % (e.message, type(e)) + " in add_conditions: " + activity.id




        def get_the_file(url, try_number = 0):
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


        #iterate through iati-activity tree
        iati_file = get_the_file(url)
        context = etree.iterparse( iati_file, tag='iati-activity' )
        fast_iter(context, process_element)
        iati_file = None
        # gc.collect()

