
from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from iati_codelists.factory import codelist_factory
from iati_vocabulary.factory import vocabulary_factory

from api.activity import serializers

from iati import models as iati_models
from iati.transaction import models as transaction_models

from lxml.builder import E
from lxml import etree as ET

from iati.factory.utils import _create_test_activity

# narrative = getattr(E, 'narrative')
iati_activities = getattr(E, 'iati-activities')
iati_activity = getattr(E, 'iati-activity')
iati_identifier = getattr(E, 'iati-identifier')
reporting_org = getattr(E, 'reporting-org')
title = getattr(E, 'title')
description = getattr(E, 'description')
participating_org = getattr(E, 'participating-org')
other_identifier = getattr(E, 'other-identifier')
activity_status = getattr(E, 'activity-status')
recipient_country = getattr(E, 'recipient-country')
recipient_region = getattr(E, 'recipient-region')
sector = getattr(E, 'sector')
document_link = getattr(E, 'document-link')
owner_org = getattr(E, 'owner-org')
transaction = getattr(E, 'transaction')
transaction_type = getattr(E, 'transaction-type')
transaction_date = getattr(E, 'transaction-date')
capital_spend = getattr(E, 'capital-spend')
value = getattr(E, 'value')
provider_org = getattr(E, 'provider-org')
receiver_org = getattr(E, 'receiver-org')
disbursement_channel = getattr(E, 'disbursement-channel')
flow_type = getattr(E, 'flow-type')
finance_type = getattr(E, 'finance-type')
aid_type = getattr(E, 'aid-type')
tied_status = getattr(E, 'tied-status')
location = getattr(E, 'location')
name = getattr(E, 'name')
location_reach = getattr(E, 'location-reach')
location_id = getattr(E, 'location-id')
activity_description = getattr(E, 'activity-description')
administrative = getattr(E, 'administrative')
point = getattr(E, 'point')
pos = getattr(E, 'pos')
exactness = getattr(E, 'exactness')
location_class = getattr(E, 'location-class')
feature_designation = getattr(E, 'feature-designation')
budget = getattr(E, 'budget')
period_start = getattr(E, 'period-start')
period_end = getattr(E, 'period-end')
conditions = getattr(E, 'conditions')
condition = getattr(E, 'condition')
contact_info = getattr(E, 'contact-info')
organisation = getattr(E, 'organisation')
department = getattr(E, 'department')
person_name = getattr(E, 'person-name')
job_title = getattr(E, 'job-title')
telephone = getattr(E, 'telephone')
email = getattr(E, 'email')
website= getattr(E, 'website')
mailing_address = getattr(E, 'mailing-address')
country_budget_items = getattr(E, 'country-budget-items')
budget_item = getattr(E, 'budget-item')


def narrative(content):
    return getattr(E, 'narrative')(content, **{
            "{http://www.w3.org/XML/1998/namespace}lang": "en",
        })

def boolToNum(b):
    if b:
        return "1"
    else:
        return "0"

class ActivityXMLTestCase(TestCase):
    """
    Test ActivityXMLSerializer outputs proper XML
    """
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        self.activity = _create_test_activity()
        # TODO: generate full activity example so we can parse this and test the result - 2016-12-14

    def test_create_activity(self):
        res = self.c.get(
                "/api/export/activities/?format=xml", 
                format='json'
                )

        activity = self.activity
        reporting_org1 = activity.reporting_organisations.all()[0]
        # reporting_org2 = activity.reporting_organisations.all()[1]
        description1 = activity.description_set.all()[0]
        description2 = activity.description_set.all()[1]
        participating_org1 = activity.participating_organisations.all()[0]
        other_identifier1 = activity.otheridentifier_set.all()[0]
        # activity_status1 = activity.activity_status
        recipient_country1 = activity.activityrecipientcountry_set.all()[0]
        recipient_region1 = activity.activityrecipientregion_set.all()[0]
        sector1 = activity.activitysector_set.all()[0]
        document_link1 = activity.documentlink_set.all()[0]
        document_link_category1 = document_link1.documentlinkcategory_set.all()[0]
        document_link_language1 = document_link1.documentlinklanguage_set.all()[0]
        location1 = activity.location_set.all()[0]
        location_administrative1= location1.locationadministrative_set.all()[0]
        transaction1 = activity.transaction_set.all()[0]
        provider_org1 = transaction1.provider_organisation
        receiver_org1 = transaction1.receiver_organisation
        transaction_sector1 = transaction1.transactionsector_set.all()[0]
        transaction_recipient_country1 = transaction1.transactionrecipientcountry_set.all()[0]
        transaction_recipient_region1 = transaction1.transactionrecipientregion_set.all()[0]
        budget1 = activity.budget_set.all()[0]
        conditions1 = activity.conditions_set.all()[0]
        condition1 = conditions1.condition_set.all()[0]
        contact_info1 = activity.contactinfo_set.all()[0]
        country_budget_item1 = activity.country_budget_items
        budget_item1 = country_budget_item1.budgetitem_set.all()[0]


        xml = iati_activities(
                iati_activity(
                        iati_identifier(activity.iati_identifier),
                        reporting_org(
                            narrative("reporting_organisation1"),
                            narrative("reporting_organisation2"),
                            **{
                                "ref": reporting_org1.ref,
                                "type": reporting_org1.type.code,
                                "secondary-reporter": boolToNum(reporting_org1.secondary_reporter)
                            }
                            ),
                        title(
                            narrative("title1"),
                            narrative("title2"),
                            ),
                        description(
                            narrative("description1_1"),
                            narrative("description1_2"),
                            **{
                                "type": description1.type.code
                            }
                            ),
                        description(
                            narrative("description2_1"),
                            narrative("description2_2"),
                            **{
                                "type": description2.type.code
                            }
                            ),
                        participating_org(
                            narrative("participating_organisation1"),
                            narrative("participating_organisation2"),
                            **{
                                "ref": participating_org1.normalized_ref,
                                "type": participating_org1.type.code,
                                "role": participating_org1.role.code,
                                "activity-id": participating_org1.org_activity_id,
                            }
                            ),
                        other_identifier(
                            owner_org(
                                narrative(other_identifier1.narratives.all()[0].content),
                                narrative(other_identifier1.narratives.all()[1].content),
                                **{
                                    "ref": other_identifier1.owner_ref,
                                }
                            ),
                            **{
                                "ref": other_identifier1.identifier,
                                "type": other_identifier1.type.code,
                            }
                            ),
                        # activity_status(
                        #     **{
                        #         "code": activity_status1.type.code
                        #     }
                        #     ),
                        contact_info(
                            organisation(
                                narrative("Agency A"),
                                ),
                            department(
                                narrative("Department B"),
                                ),
                            person_name(
                                narrative("A. Example"),
                                ),
                            job_title(
                                narrative("Transparency Lead"),
                                ),
                            telephone(contact_info1.telephone),
                            email(contact_info1.email),
                            website(contact_info1.website),
                            mailing_address(
                                narrative("Transparency House, The Street, Town, City, Postcode")
                                ), 
                            ** {
                            "type": contact_info1.type.code,
                            }),
                        recipient_country(
                            # narrative("recipient_country1"),
                            # narrative("recipient_country2"),
                            **{
                                "code": recipient_country1.country.code,
                                "percentage": str(recipient_country1.percentage),
                            }
                            ),
                        recipient_region(
                            # narrative("recipient_region1"),
                            # narrative("recipient_region2"),
                            **{
                                "code": recipient_region1.region.code,
                                "vocabulary": recipient_region1.vocabulary.code,
                                "vocabulary-uri": recipient_region1.vocabulary_uri,
                                "percentage": str(recipient_region1.percentage)
                            }
                            ),
                        location(
                            location_reach(code=location1.location_reach.code),
                            location_id(**{
                                "vocabulary": location1.location_id_vocabulary.code,
                                "code": location1.location_id_code,
                            }),
                            name(
                                narrative("location_name1_1"),
                                ),
                            description(
                                narrative("location_description1_1"),
                                ),
                            activity_description(
                                narrative("location_activity_description1_1"),
                                ),
                            administrative(**{
                                "vocabulary": location_administrative1.vocabulary.code,
                                "code": location_administrative1.code,
                                "level": str(location_administrative1.level),
                            }),
                            point(
                                pos(
                                    "{} {}".format(location1.point_pos.y, location1.point_pos.x)),
                                **{
                                    "srsName": location1.point_srs_name,
                                }
                                ),
                            exactness(code=location1.exactness.code),
                            location_class(code=location1.location_class.code),
                            feature_designation(code=location1.feature_designation.code),
                            **{
                                "ref": location1.ref,
                            }
                                ),
                        sector(
                            # narrative("sector1"),
                            # narrative("sector2"),
                            **{
                                "code": sector1.sector.code,
                                "vocabulary": sector1.vocabulary.code,
                                "vocabulary-uri": sector1.vocabulary_uri,
                                "percentage": str(sector1.percentage),
                            }
                            ),
                        country_budget_items(
                            budget_item(
                                description(
                                    narrative("Description text"),
                                    ),
                                **{"code": budget_item1.code.code}
                                ),
                            **{"vocabulary": country_budget_item1.vocabulary.code}
                            ),
                            budget(
                                period_start(**{'iso-date': budget1.period_start.isoformat()}),
                                period_end(**{'iso-date': budget1.period_end.isoformat()}),
                                value(
                                    str(budget1.value),
                                    **{
                                    'currency': budget1.currency.code, 
                                    'value-date': budget1.value_date.isoformat(),
                                    }),
                            **{
                            "type": budget1.type.code,
                            "status": budget1.status.code,
                            }),
                        capital_spend(
                            **{
                                "percentage": str(activity.capital_spend),
                            }
                            ),
                        transaction(
                            transaction_type(code=transaction1.transaction_type.code),
                            transaction_date(**{ 'iso-date': transaction1.transaction_date.isoformat() }),
                            value(str(transaction1.value), **{
                                "currency": transaction1.currency.code,
                                "value-date": transaction1.value_date.isoformat()
                            }),
                            description(
                                narrative("transaction_description1_1"),
                                narrative("transaction_description1_2"),
                                ),
                            provider_org(
                                narrative("transaction_provider_org1_1"),
                                narrative("transaction_provider_org1_2"),
                                **{
                                    "provider-activity-id": provider_org1.provider_activity_ref,
                                    "ref": provider_org1.ref,
                                }),
                            receiver_org(
                                narrative("transaction_receiver_org1_1"),
                                narrative("transaction_receiver_org1_2"),
                                **{
                                    "receiver-activity-id": receiver_org1.receiver_activity_ref,
                                    "ref": receiver_org1.ref,
                                }),
                            disbursement_channel(code=transaction1.disbursement_channel.code),
                            sector(**{
                                "vocabulary": transaction_sector1.vocabulary.code,
                                "vocabulary-uri": transaction_sector1.vocabulary_uri,
                                "code": transaction_sector1.sector.code,
                            }),
                            recipient_country(**{
                                "code": transaction_recipient_country1.country.code,
                            }),
                            recipient_region(**{
                                "vocabulary": transaction_recipient_region1.vocabulary.code,
                                "vocabulary-uri": transaction_recipient_region1.vocabulary_uri,
                                "code": transaction_recipient_region1.region.code,
                            }),
                            flow_type(code=transaction1.flow_type.code),
                            finance_type(code=transaction1.finance_type.code),
                            aid_type(code=transaction1.aid_type.code),
                            tied_status(code=transaction1.tied_status.code),
                            **{
                                "ref": transaction1.ref,
                                "humanitarian": boolToNum(transaction1.humanitarian)
                            }),
                        document_link(
                            title(
                                narrative("document_link_title1"),
                                narrative("document_link_title2"),
                                ),
                            E.category(code=document_link_category1.category.code),
                            E.language(code=document_link_language1.language.code),
                            getattr(E, 'document-date')(**{ "iso-date": document_link1.iso_date.isoformat() }),
                            **{
                                "format": document_link1.file_format.code,
                                "url": document_link1.url,
                            }
                            ),
                        conditions(
                            condition(
                                narrative("Conditions text"),
                                narrative("Conditions texte"),
                                **{"type": condition1.type.code,}),
                            **{"attached": boolToNum(conditions1.attached),}
                            ),
                        **{
                            "hierarchy": str(activity.hierarchy),
                            "{http://www.w3.org/XML/1998/namespace}lang": activity.default_lang.code,
                        }
                    ),
                    version="2.02",
                )

        parsed_xml = ET.fromstring(res.content)

        print("ORIGINAL")
        print(ET.tostring(xml, pretty_print=True))

        #print contact_info1.mailing_address.narratives.all()[0]
        #print budget_item1.description.narratives.all()[0]

        print("PARSED")
        print(ET.tostring(parsed_xml))

        def elements_equal(e1, e2):
            self.assertEqual(e1.tag, e2.tag)
            self.assertEqual(e1.text, e2.text)
            self.assertEqual(e1.tail, e2.tail)
            self.assertEqual(e1.attrib, e2.attrib)
            self.assertEqual(len(e1), len(e2), "{} != {} for elements {} and {}".format(len(e1), len(e2), e1.tag, e2.tag))
            return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

        elements_equal(ET.fromstring(ET.tostring(xml, pretty_print=True)), parsed_xml)

