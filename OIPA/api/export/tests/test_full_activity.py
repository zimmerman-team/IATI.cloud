
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
humanitarian_scope = getattr(E, 'humanitarian-scope')
legacy_data = getattr(E, 'legacy-data')
crs_add = getattr(E, 'crs-add')
other_flags = getattr(E, 'other-flags')
loan_terms = getattr(E, 'loan-terms')
repayment_type = getattr(E, 'repayment-type')
repayment_plan = getattr(E, 'repayment-plan')
commitment_date = getattr(E, 'commitment-date')
repayment_first_date = getattr(E, 'repayment-first-date')
repayment_final_date = getattr(E, 'repayment-final-date')
loan_status = getattr(E, 'loan-status')
interest_received = getattr(E, 'interest-received')
principal_outstanding = getattr(E, 'principal-outstanding')
principal_arrears = getattr(E, 'principal-arrears')
interest_arrears = getattr(E, 'interest-arrears')
channel_code = getattr(E, 'channel-code')
collaboration_type = getattr(E, 'collaboration-type')
default_flow_type = getattr(E, 'default-flow-type')
default_finance_type = getattr(E, 'default-finance-type')
default_aid_type = getattr(E, 'default-aid-type')
default_tied_status = getattr(E, 'default-tied-status')
related_activity = getattr(E, 'related-activity')
activity_scope = getattr(E,'activity-scope')
policy_marker = getattr(E,'policy-marker')
activity_date = getattr(E,'activity-date')
planned_disbursement = getattr(E,'planned-disbursement')
result = getattr(E, 'result')
period = getattr(E,'period')
indicator = getattr(E,'indicator')
reference = getattr(E,'reference')
baseline = getattr(E,'baseline')
comment = getattr(E,'comment')
target = getattr(E,'target')
dimension = getattr(E,'dimension')
actual = getattr(E,'actual')
fss = getattr(E, 'fss')
forecast  = getattr(E, 'forecast')



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
                "/api/export/activities/IATI-search1?format=xml", 
                format='json'
                )

        activity = self.activity
        reporting_org1 = activity.publisher.organisation.reporting_org
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
        transaction_recipient_country1 = transaction1.recipient_country.all()[0]
        transaction_recipient_region1 = transaction1.transactionrecipientregion_set.all()[0]
        budget1 = activity.budget_set.all()[0]
        conditions1 = activity.conditions
        condition1 = conditions1.condition_set.all()[0]
        condition2 = conditions1.condition_set.all()[1]
        # conditions2 = activity.conditions_set.all()[1]
        # condition3 = conditions2.condition_set.all()[0]
        # condition4 = conditions2.condition_set.all()[1]
        contact_info1 = activity.contactinfo_set.all()[0]
        country_budget_item1 = activity.country_budget_items
        budget_item1 = country_budget_item1.budgetitem_set.all()[0]
        humanitarian_scope1 = activity.humanitarianscope_set.all()[0]
        legacy_data1 = activity.legacydata_set.all()[0]
        legacy_data2 = activity.legacydata_set.all()[1]
        crs_add1 = activity.crsadd_set.all()[0]
        other_flag1 = crs_add1.other_flags.all()[0]
        crs_add_loan_terms1 = crs_add1.loan_terms
        related_activity1 = activity.relatedactivity_set.all()[0]
        policy_marker1 = activity.activitypolicymarker_set.all()[0]
        activity_date1 = activity.activitydate_set.all()[0]
        planned_disbursement1 = activity.planneddisbursement_set.all()[0]
        planned_disbursement_provider1 = planned_disbursement1.provider_organisation
        planned_disbursement_receiver1 = planned_disbursement1.receiver_organisation
        result1 = activity.result_set.all()[0]
        result_indicator1 = result1.resultindicator_set.all()[0]
        result_indicator_reference1 = result_indicator1.resultindicatorreference_set.all()[0]
        result_indicator_period1 = result_indicator1.resultindicatorperiod_set.all()[0]
        result_indicator_period_target_location1 = result_indicator_period1.resultindicatorperiodtargetlocation_set.all()[0]
        result_indicator_period_target_dimension1 = result_indicator_period1.resultindicatorperiodtargetdimension_set.all()[0]
        result_indicator_period_target_comment1 = result_indicator_period1.resultindicatorperiodtargetcomment

        result_indicator_period_actual_location1 = result_indicator_period1.resultindicatorperiodactuallocation_set.all()[0]
        result_indicator_period_actual_dimension1 = result_indicator_period1.resultindicatorperiodactualdimension_set.all()[0]
        result_indicator_period_actual_comment1 = result_indicator_period1.resultindicatorperiodactualcomment

        location01 = related_activity1.ref_activity.location_set.all()[0]
        location02 = related_activity1.ref_activity.location_set.all()[1]

        fss1 = activity.fss_set.all()[0]
        fss_forecast1 = fss1.fssforecast_set.all()[0]


        xml = iati_activities(
                iati_activity(
                    iati_identifier(related_activity1.ref_activity.iati_identifier),
                    reporting_org(
                        narrative("reporting_organisation1"),
                        narrative("reporting_organisation2"),
                        **{
                            "ref": reporting_org1.organisation.organisation_identifier,
                            "type": reporting_org1.org_type.code,
                            "secondary-reporter": boolToNum(reporting_org1.secondary_reporter)
                        }
                        ),
                    activity_status(**{"code": str(related_activity1.ref_activity.activity_status.code)}),
                    activity_scope(**{"code": str(related_activity1.ref_activity.scope.code)}),
                    location(
                        location_reach(code=location01.location_reach.code),
                        location_id(**{
                            "vocabulary": location01.location_id_vocabulary.code,
                            "code": location01.location_id_code,
                        }),
                        name(),
                        description(),
                        activity_description(),
                        point(
                            pos(
                                "{} {}".format(location01.point_pos.y, location01.point_pos.x)),
                            **{
                                "srsName": location01.point_srs_name,
                            }
                            ),
                        exactness(code=location01.exactness.code),
                        location_class(code=location01.location_class.code),
                        feature_designation(code=location01.feature_designation.code),
                        **{
                            "ref": location01.ref,
                        }
                        ),
                    location(
                        location_reach(code=location02.location_reach.code),
                        location_id(**{
                            "vocabulary": location02.location_id_vocabulary.code,
                            "code": location02.location_id_code,
                        }),
                        name(),
                        description(),
                        activity_description(),
                        point(
                            pos(
                                "{} {}".format(location02.point_pos.y, location02.point_pos.x)),
                            **{
                                "srsName": location02.point_srs_name,
                            }
                            ),
                        exactness(code=location02.exactness.code),
                        location_class(code=location02.location_class.code),
                        feature_designation(code=location02.feature_designation.code),
                        **{
                            "ref": location02.ref,
                        }
                        ),
                    collaboration_type(**{"code": str(related_activity1.ref_activity.collaboration_type.code)}),
                    default_flow_type(**{"code": str(related_activity1.ref_activity.default_flow_type.code)}),
                    default_finance_type(**{"code": str(related_activity1.ref_activity.default_finance_type.code)}),
                    default_aid_type(**{"code": str(related_activity1.ref_activity.default_aid_type.code)}),
                    default_tied_status(**{"code": str(related_activity1.ref_activity.default_tied_status.code)}),
                    **{
                            "hierarchy": str(related_activity1.ref_activity.hierarchy),
                            "{http://www.w3.org/XML/1998/namespace}lang": related_activity1.ref_activity.default_lang.code,
                    }
                    ),
                iati_activity(
                        iati_identifier(activity.iati_identifier),
                        reporting_org(
                            narrative("reporting_organisation1"),
                            narrative("reporting_organisation2"),
                            **{
                                "ref": reporting_org1.organisation.organisation_identifier,
                                "type": reporting_org1.org_type.code,
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
                        activity_status(**{"code": str(activity.activity_status.code)}),
                        activity_date(
                            **{
                            "iso-date": activity_date1.iso_date.isoformat(),
                            "type": activity_date1.type.code
                            }),
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
                        activity_scope(
                            **{"code": str(activity.scope.code)}),
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
                        humanitarian_scope(
                            # Add HumanitarianScope in data models Date 12-01-2017
                            # narrative("Nepal Earthquake April 2015"),
                            **{
                            "type": humanitarian_scope1.type.code,
                            "vocabulary": humanitarian_scope1.vocabulary.code,
                            "code": humanitarian_scope1.code
                            }),
                        policy_marker(
                                **{
                                "vocabulary": policy_marker1.vocabulary.code,
                                "code": policy_marker1.code.code,
                                "significance": policy_marker1.significance.code
                                }
                                ),
                        collaboration_type(**{"code": str(activity.collaboration_type.code)}),
                        default_flow_type(**{"code": str(activity.default_flow_type.code)}),
                        default_finance_type(**{"code": str(activity.default_finance_type.code)}),
                        default_aid_type(**{"code": str(activity.default_aid_type.code)}),
                        default_tied_status(**{"code": str(activity.default_tied_status.code)}),
                        planned_disbursement(
                            period_start(**{"iso-date": planned_disbursement1.period_start.isoformat()}),
                            period_end(**{"iso-date": planned_disbursement1.period_end.isoformat()}),
                            value(
                                str(planned_disbursement1.value),
                                **{
                                "currency": planned_disbursement1.currency.code,
                                "value-date": planned_disbursement1.value_date.isoformat()
                                }),
                            provider_org(
                                narrative("Agency B"),
                                **{
                                "provider-activity-id": planned_disbursement_provider1.provider_activity_ref,
                                "type": planned_disbursement_provider1.type.code,
                                "ref": planned_disbursement_provider1.ref
                                }),
                            receiver_org(
                                narrative("Agency A"),
                                **{
                                "receiver-activity-id":planned_disbursement_receiver1.receiver_activity_ref,
                                "type": planned_disbursement_receiver1.type.code,
                                "ref":planned_disbursement_receiver1.ref
                                }),
                            **{"type": planned_disbursement1.type.code}
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
                        related_activity(**{
                            "ref": related_activity1.ref,
                            "type": str(related_activity1.type.code)
                            }),
                        legacy_data(
                            **{
                            "name": legacy_data1.name,
                            "value": legacy_data1.value,
                            "iati-equivalent": legacy_data1.iati_equivalent
                            }
                            ),
                        legacy_data(
                            **{
                            "name": legacy_data2.name,
                            "value": legacy_data2.value,
                            "iati-equivalent": legacy_data2.iati_equivalent
                            }
                            ),
                        conditions(
                            condition(
                                narrative("Conditions text"),
                                narrative("Conditions texte"),
                                **{"type": condition1.type.code,}
                                ),
                            condition(
                                narrative("Conditions text2"),
                                narrative("Conditions texte2"),
                                **{"type": condition2.type.code,}
                                ),
                            **{"attached": boolToNum(conditions1.attached),}
                            ),
                        # conditions(
                        #     condition(
                        #         narrative("Conditions text3"),
                        #         narrative("Conditions texte3"),
                        #         **{"type": condition1.type.code,}
                        #         ),
                        #     condition(
                        #         narrative("Conditions text4"),
                        #         narrative("Conditions texte4"),
                        #         **{"type": condition2.type.code,}
                        #         ),
                        #     **{"attached": boolToNum(conditions2.attached),}
                        #     ),
                        result(
                            title(narrative("Result title")),
                            description(narrative("Result description text")),
                            indicator(
                                title(narrative("Indicator title")),
                                description(narrative("Indicator description text")),
                                reference(
                                    **{
                                    "vocabulary": result_indicator_reference1.vocabulary.code,
                                    "code": result_indicator_reference1.code,
                                    "indicator-uri": result_indicator_reference1.indicator_uri
                                    }),
                                baseline(
                                    comment(narrative("Baseline comment text")),
                                    **{
                                    "year": str(result_indicator1.baseline_year),
                                    "value": result_indicator1.baseline_value
                                    }),
                                period(
                                    period_start(**{"iso-date":result_indicator_period1.period_start.isoformat()}),
                                    period_end(**{"iso-date": result_indicator_period1.period_end.isoformat()}),
                                    target(
                                        comment(narrative("Target comment text")),
                                        location(**{"ref": result_indicator_period_target_location1.ref}),
                                        dimension(**{
                                            "name": result_indicator_period_target_dimension1.name, 
                                            "value": result_indicator_period_target_dimension1.value
                                            }),
                                        **{"value": str(result_indicator_period1.target)}
                                        ),
                                    actual(
                                        comment(narrative("Actual comment text")),
                                        location(**{"ref": result_indicator_period_actual_location1.ref}),
                                        dimension(**{
                                            "name": result_indicator_period_actual_dimension1.name,
                                            "value":result_indicator_period_actual_dimension1.value
                                            }),
                                        **{"value": str(result_indicator_period1.actual)}
                                        )
                                    ),
                                **{
                                "measure": result_indicator1.measure.code,
                                "ascending": boolToNum(result_indicator1.ascending)
                                }),
                            **{
                            "type": result1.type.code,
                            "aggregation-status": boolToNum(result1.aggregation_status)
                            }),
                        crs_add(
                            other_flags(
                                **{
                                "code": other_flag1.other_flags.code,
                                "significance": boolToNum(other_flag1.significance)
                                }
                            ),
                            loan_terms(
                                repayment_type(
                                    **{
                                    "code":crs_add1.loan_terms.repayment_type.code
                                    }
                                    ),
                                repayment_plan(
                                    **{
                                    "code":crs_add1.loan_terms.repayment_plan.code
                                    }
                                    ),
                                commitment_date(
                                    **{
                                    "iso-date":str(crs_add1.loan_terms.commitment_date)
                                    }
                                    ),
                                repayment_first_date(
                                    **{
                                    "iso-date":str(crs_add1.loan_terms.repayment_first_date)
                                    }
                                    ),
                                repayment_final_date(
                                    **{
                                    "iso-date":str(crs_add1.loan_terms.repayment_final_date)
                                    }
                                    ),
                                **{
                                "rate-1":str(crs_add1.loan_terms.rate_1),
                                "rate-2":str(crs_add1.loan_terms.rate_2)
                                }
                                ),
                            loan_status(
                                interest_received(str(crs_add1.loan_status.interest_received)),
                                principal_outstanding(str(crs_add1.loan_status.principal_outstanding)),
                                principal_arrears(str(crs_add1.loan_status.principal_arrears)),
                                interest_arrears(str(crs_add1.loan_status.interest_arrears)),
                                **{
                                "year": str(crs_add1.loan_status.year),
                                "currency":crs_add1.loan_status.currency.code,
                                "value-date": str(crs_add1.loan_status.value_date)
                                }
                                ),
                            channel_code(crs_add1.channel_code)
                            ),
                        fss(
                            forecast(
                                str(fss_forecast1.value),
                                **{
                                "year": str(fss_forecast1.year),
                                "value-date": fss_forecast1.value_date.isoformat(),
                                "currency": str(fss_forecast1.currency.code)
                                }),
                            **{
                            "extraction-date": fss1.extraction_date.isoformat(),
                            "priority": boolToNum(fss1.priority),
                            "phaseout-year": str(fss1.phaseout_year)
                            }),
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

        # print contact_info1.mailing_address.narratives.all()[0]
        # print budget_item1.description.narratives.all()[0]
        #print planned_disbursement_provider1.narratives.all()[0]
        # print result1.resulttitle.narratives.all()[0]


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

