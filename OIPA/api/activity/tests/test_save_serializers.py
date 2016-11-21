
# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from iati_codelists.factory import codelist_factory
from api.activity import serializers
from iati import models as iati_models
from iati.transaction import models as transaction_models
from django.core.exceptions import ObjectDoesNotExist


class ActivitySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_activity(self):

        iati_version = codelist_factory.VersionFactory.create(code="2.02")
        language = codelist_factory.LanguageFactory.create()
        activity_status = codelist_factory.ActivityStatusFactory.create()
        activity_scope = codelist_factory.ActivityScopeFactory.create()
        collaboration_type = codelist_factory.CollaborationTypeFactory.create()
        default_flow_type = codelist_factory.FlowTypeFactory.create()
        default_finance_type = codelist_factory.FinanceTypeFactory.create()
        default_aid_type = codelist_factory.AidTypeFactory.create()
        default_tied_status = codelist_factory.TiedStatusFactory.create()

        data = {
            "iati_identifier": 'IATI-0001',
            'iati_standard_version': {
                "code": iati_version.code, # should be ignored
                "name": 'irrelevant',
            },
            "humanitarian": "1", 
            "xml_lang": "en",
            'activity_status': {
                "code": activity_status.code, # should be ignored
                "name": 'irrelevant',
            },
            'activity_scope': {
                "code": activity_scope.code, # should be ignored
                "name": 'irrelevant',
            },
            'collaboration_type': {
                "code": collaboration_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_flow_type': {
                "code": default_flow_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_finance_type': {
                "code": default_finance_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_aid_type': {
                "code": default_aid_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_tied_status': {
                "code": default_tied_status.code, # should be ignored
                "name": 'irrelevant',
            },
            "title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },

        }

        res = self.c.post(
                "/api/activities/?format=json", 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Activity.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.iati_identifier, data['iati_identifier'])
        self.assertEqual(instance.id, data['iati_identifier'])
        self.assertEqual(instance.iati_standard_version.code, "2.02")
        self.assertEqual(instance.humanitarian, bool(data['humanitarian']))
        self.assertEqual(instance.activity_status.code, str(data['activity_status']['code']))
        self.assertEqual(instance.scope.code, str(data['activity_scope']['code']))
        self.assertEqual(instance.collaboration_type.code, str(data['collaboration_type']['code']))
        self.assertEqual(instance.default_flow_type.code, str(data['default_flow_type']['code']))
        self.assertEqual(instance.default_finance_type.code, str(data['default_finance_type']['code']))
        self.assertEqual(instance.default_aid_type.code, str(data['default_aid_type']['code']))
        self.assertEqual(instance.default_tied_status.code, str(data['default_tied_status']['code']))

        title = instance.title
        title_narratives = title.narratives.all()
        self.assertEqual(title_narratives[0].content, data['title']['narratives'][0]['text'])
        self.assertEqual(title_narratives[1].content, data['title']['narratives'][1]['text'])

    def test_update_activity(self):
        activity = iati_factory.ActivityFactory.create()

        iati_version = codelist_factory.VersionFactory.create(code="2.02")
        activity_status = codelist_factory.ActivityStatusFactory.create()
        activity_scope = codelist_factory.ActivityScopeFactory.create()
        collaboration_type = codelist_factory.CollaborationTypeFactory.create()
        default_flow_type = codelist_factory.FlowTypeFactory.create()
        default_finance_type = codelist_factory.FinanceTypeFactory.create()
        default_aid_type = codelist_factory.AidTypeFactory.create()
        default_tied_status = codelist_factory.TiedStatusFactory.create()

        data = {
            "iati_identifier": 'IATI-0001',
            'iati_standard_version': {
                "code": iati_version.code, # should be ignored
                "name": 'irrelevant',
            },
            "humanitarian": "1", 
            'activity_status': {
                "code": activity_status.code, # should be ignored
                "name": 'irrelevant',
            },
            'activity_scope': {
                "code": activity_scope.code, # should be ignored
                "name": 'irrelevant',
            },
            'collaboration_type': {
                "code": collaboration_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_flow_type': {
                "code": default_flow_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_finance_type': {
                "code": default_finance_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_aid_type': {
                "code": default_aid_type.code, # should be ignored
                "name": 'irrelevant',
            },
            'default_tied_status': {
                "code": default_tied_status.code, # should be ignored
                "name": 'irrelevant',
            },
            "xml_lang": "en",
            "title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },

        }

        res = self.c.put(
                "/api/activities/{}/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Activity.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.iati_identifier, data['iati_identifier'])
        self.assertEqual(instance.id, data['iati_identifier'])
        self.assertEqual(instance.iati_standard_version.code, "2.02")
        self.assertEqual(instance.humanitarian, bool(data['humanitarian']))
        self.assertEqual(instance.activity_status.code, str(data['activity_status']['code']))
        self.assertEqual(instance.scope.code, str(data['activity_scope']['code']))
        self.assertEqual(instance.collaboration_type.code, str(data['collaboration_type']['code']))
        self.assertEqual(instance.default_flow_type.code, str(data['default_flow_type']['code']))
        self.assertEqual(instance.default_finance_type.code, str(data['default_finance_type']['code']))
        self.assertEqual(instance.default_aid_type.code, str(data['default_aid_type']['code']))
        self.assertEqual(instance.default_tied_status.code, str(data['default_tied_status']['code']))

        title = instance.title
        title_narratives = title.narratives.all()
        self.assertEqual(title_narratives[0].content, data['title']['narratives'][0]['text'])
        self.assertEqual(title_narratives[1].content, data['title']['narratives'][1]['text'])

    def test_delete_activity(self):
        activity = iati_factory.ActivityFactory.create()

        res = self.c.delete(
                "/api/activities/{}/?format=json".format(activity.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Activity.objects.get(pk=activity.id)


class ReportingOrganisationSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_reporting_organisation(self):

        activity = iati_factory.ActivityFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        iati_factory.OrganisationTypeFactory.create(code=9)
        iati_factory.OrganisationRoleFactory.create(code=1)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": activity.id,
            "organisation": organisation.id,
            "type": {
                "code": '9',
                "name": 'irrelevant',
            },
            "secondary_reporter": 1,
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.post(
                "/api/activities/{}/reporting_organisations/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityReportingOrganisation.objects.get(ref=data['ref'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.secondary_reporter, bool(data['secondary_reporter']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])

    def test_update_reporting_organisation(self):
        reporting_org = iati_factory.ReportingOrganisationFactory.create()
        iati_factory.OrganisationTypeFactory.create(code=9)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": reporting_org.activity.id,
            "organisation": reporting_org.organisation.id,
            "type": {
                "code": '9',
                "name": 'irrelevant',
            },
            "secondary_reporter": 1,
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.put(
                "/api/activities/{}/reporting_organisations/{}?format=json".format(reporting_org.activity.id, reporting_org.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityReportingOrganisation.objects.get(ref=data['ref'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.secondary_reporter, bool(data['secondary_reporter']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])

    def test_delete_reporting_organisation(self):
        reporting_org = iati_factory.ReportingOrganisationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/reporting_organisations/{}?format=json".format(reporting_org.activity.id, reporting_org.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityReportingOrganisation.objects.get(ref=reporting_org.ref)

class DescriptionSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_description(self):

        activity = iati_factory.ActivityFactory.create()
        type = iati_factory.DescriptionTypeFactory.create()
        # type = iati_factory.DescriptionTypeFactory.create(code=2)

        data = {
            "activity": activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.post(
                "/api/activities/{}/descriptions/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Description.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])


    def test_update_description(self):
        description = iati_factory.DescriptionFactory.create()
        type = iati_factory.DescriptionTypeFactory.create()
        type2 = iati_factory.DescriptionTypeFactory.create(code=2)

        data = {
            "activity": description.activity.id,
            "type": {
                "code": type2.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.put(
                "/api/activities/{}/descriptions/{}?format=json".format(description.activity.id, description.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Description.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, str(data['type']['code']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])


    def test_delete_description(self):
        description = iati_factory.DescriptionFactory.create()

        res = self.c.delete(
                "/api/activities/{}/descriptions/{}?format=json".format(description.activity.id, description.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Description.objects.get(pk=description.id)


class ParticipatingOrganisationSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_participating_organisation(self):

        activity = iati_factory.ActivityFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        org_type = iati_factory.OrganisationTypeFactory.create(code=9)
        org_role = iati_factory.OrganisationRoleFactory.create(code=1)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": activity.id,
            "organisation": organisation.id,
            "type": {
                "code": org_type.code,
                "name": 'irrelevant',
            },
            "role": {
                "code": org_role.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.post(
                "/api/activities/{}/participating_organisations/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityParticipatingOrganisation.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, str(data['type']['code']))
        self.assertEqual(instance.role.code, str(data['role']['code']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])

    def test_update_participating_organisation(self):
        participating_org = iati_factory.ParticipatingOrganisationFactory.create()
        
        org_type = iati_factory.OrganisationTypeFactory.create(code=22)
        org_role = iati_factory.OrganisationRoleFactory.create(code=22)

        data = {
            "ref": 'GB-COH-03580586',
            "activity": participating_org.activity.id,
            "organisation": participating_org.organisation.id,
            "type": {
                "code": org_type.code,
                "name": 'irrelevant',
            },
            "role": {
                "code": org_role.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.put(
                "/api/activities/{}/participating_organisations/{}?format=json".format(participating_org.activity.id, participating_org.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityParticipatingOrganisation.objects.get(ref=data['ref'])

        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.type.code, str(data['type']['code']))
        self.assertEqual(instance.role.code, str(data['role']['code']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])


    def test_delete_participating_organisation(self):
        participating_org = iati_factory.ParticipatingOrganisationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/participating_organisations/{}?format=json".format(participating_org.activity.id, participating_org.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityParticipatingOrganisation.objects.get(pk=participating_org.id)


class ActivityDateSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_activity_date(self):

        activity = iati_factory.ActivityFactory.create()
        type = iati_factory.ActivityDateTypeFactory.create()

        data = {
            "activity": activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "iso_date": datetime.datetime.now().isoformat(' '),
        }

        res = self.c.post(
                "/api/activities/{}/activity_dates/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityDate.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])

    def test_update_activity_date(self):
        activity_date = iati_factory.ActivityDateFactory.create()
        type = iati_factory.ActivityDateTypeFactory.create()
        type2 = iati_factory.ActivityDateTypeFactory.create(code=2)

        data = {
            "activity": activity_date.activity.id,
            "type": {
                "code": type2.code,
                "name": 'irrelevant',
            },
            "iso_date": datetime.datetime.now().isoformat(' '),
        }

        res = self.c.put(
                "/api/activities/{}/activity_dates/{}?format=json".format(activity_date.activity.id, activity_date.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityDate.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, str(data['type']['code']))

    def test_delete_activity_dates(self):
        activity_dates = iati_factory.ActivityDateFactory.create()

        res = self.c.delete(
                "/api/activities/{}/activity_dates/{}?format=json".format(activity_dates.activity.id, activity_dates.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityDate.objects.get(pk=activity_dates.id)


class ContactInfoSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_contact_info(self):

        activity = iati_factory.ActivityFactory.create()
        contact_type = iati_factory.ContactTypeFactory.create()
        # organisation = iati_factory.ContactInfoOrganisationFactory.create()
        # department = iati_factory.ContactInfoDepartmentFactory.create()
        # person_name = iati_factory.ContactInfoPersonNameFactory.create()
        # job_title = iati_factory.ContactInfoJobTitleFactory.create()
        # telephone = iati_factory.ContactInfoTelephoneFactory.create()
        # email = iati_factory.ContactInfoEmailFactory.create()
        # website = iati_factory.ContactInfoWebsiteFactory.create()
        # mailing_address = iati_factory.ContactInfoMailingAddressFactory.create()

        data = {
            "activity": activity.id,
            "type": {
                "code": contact_type.code,
                "name": "irrelevant"
            },
            "organisation": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "department": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "person_name": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "job_title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "telephone": "0631942897",
            "email": "test@zz.com",
            "website": "https://zimmermanzimmerman.com",
            "mailing_address": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            }
        }

        res = self.c.post(
                "/api/activities/{}/contact_info/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ContactInfo.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])

        organisation_narratives = instance.organisation.narratives.all()
        self.assertEqual(organisation_narratives[0].content, data['organisation']['narratives'][0]['text'])
        self.assertEqual(organisation_narratives[1].content, data['organisation']['narratives'][1]['text'])

        department_narratives = instance.department.narratives.all()
        self.assertEqual(department_narratives[0].content, data['department']['narratives'][0]['text'])
        self.assertEqual(department_narratives[1].content, data['department']['narratives'][1]['text'])

        person_name_narratives = instance.person_name.narratives.all()
        self.assertEqual(person_name_narratives[0].content, data['person_name']['narratives'][0]['text'])
        self.assertEqual(person_name_narratives[1].content, data['person_name']['narratives'][1]['text'])

        job_title_narratives = instance.job_title.narratives.all()
        self.assertEqual(job_title_narratives[0].content, data['job_title']['narratives'][0]['text'])
        self.assertEqual(job_title_narratives[1].content, data['job_title']['narratives'][1]['text'])

        mailing_address_narratives = instance.mailing_address.narratives.all()
        self.assertEqual(mailing_address_narratives[0].content, data['mailing_address']['narratives'][0]['text'])
        self.assertEqual(mailing_address_narratives[1].content, data['mailing_address']['narratives'][1]['text'])

    def test_update_contact_info(self):
        contact_info = iati_factory.ContactInfoFactory.create()
        contact_type = iati_factory.ContactTypeFactory.create()

        data = {
            "activity": contact_info.activity.id,
            "type": {
                "code": contact_type.code,
                "name": "irrelevant"
            },
            "organisation": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "department": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "person_name": {
                "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
            },
            "job_title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "telephone": "0631942897",
            "email": "test@zz.com",
            "website": "https://zimmermanzimmerman.com",
            "mailing_address": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            }
        }

        res = self.c.put(
                "/api/activities/{}/contact_info/{}?format=json".format(contact_info.activity.id, contact_info.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ContactInfo.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])

        organisation_narratives = instance.organisation.narratives.all()
        self.assertEqual(organisation_narratives[0].content, data['organisation']['narratives'][0]['text'])
        self.assertEqual(organisation_narratives[1].content, data['organisation']['narratives'][1]['text'])

        department_narratives = instance.department.narratives.all()
        self.assertEqual(department_narratives[0].content, data['department']['narratives'][0]['text'])
        self.assertEqual(department_narratives[1].content, data['department']['narratives'][1]['text'])

        person_name_narratives = instance.person_name.narratives.all()
        self.assertEqual(person_name_narratives[0].content, data['person_name']['narratives'][0]['text'])
        self.assertEqual(person_name_narratives[1].content, data['person_name']['narratives'][1]['text'])

        job_title_narratives = instance.job_title.narratives.all()
        self.assertEqual(job_title_narratives[0].content, data['job_title']['narratives'][0]['text'])
        self.assertEqual(job_title_narratives[1].content, data['job_title']['narratives'][1]['text'])

        mailing_address_narratives = instance.mailing_address.narratives.all()
        self.assertEqual(mailing_address_narratives[0].content, data['mailing_address']['narratives'][0]['text'])
        self.assertEqual(mailing_address_narratives[1].content, data['mailing_address']['narratives'][1]['text'])


    def test_delete_contact_info(self):
        contact_infos = iati_factory.ContactInfoFactory.create()

        res = self.c.delete(
                "/api/activities/{}/contact_info/{}?format=json".format(contact_infos.activity.id, contact_infos.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ContactInfo.objects.get(pk=contact_infos.id)


class ActivityRecipientCountrySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_recipient_country(self):

        activity = iati_factory.ActivityFactory.create()
        country = iati_factory.CountryFactory.create()

        data = {
            "activity": activity.id,
            "country": {
                "code": country.code,
                "name": 'irrelevant',
            },
            "percentage": 100,
        }

        res = self.c.post(
                "/api/activities/{}/recipient_countries/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityRecipientCountry.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.country.code, data['country']['code'])
        self.assertEqual(instance.percentage, data['percentage'])

    def test_update_recipient_country(self):
        recipient_country = iati_factory.ActivityRecipientCountryFactory.create()
        country = iati_factory.CountryFactory.create(code='AF')

        data = {
            "activity": recipient_country.activity.id,
            "country": {
                "code": country.code,
                "name": 'irrelevant',
            },
            "percentage": 100,
        }

        res = self.c.put(
                "/api/activities/{}/recipient_countries/{}?format=json".format(recipient_country.activity.id, recipient_country.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityRecipientCountry.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.country.code, str(data['country']['code']))
        self.assertEqual(instance.percentage, data['percentage'])

    def test_delete_recipient_country(self):
        recipient_country = iati_factory.ActivityRecipientCountryFactory.create()

        res = self.c.delete(
                "/api/activities/{}/recipient_countries/{}?format=json".format(recipient_country.activity.id, recipient_country.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityRecipientCountry.objects.get(pk=recipient_country.id)




class ActivityRecipientRegionSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_recipient_region(self):

        activity = iati_factory.ActivityFactory.create()
        region = iati_factory.RegionFactory.create()
        region_vocabulary = iati_factory.RegionVocabularyFactory.create()

        data = {
            "activity": activity.id,
            "region": {
                "code": region.code,
                "name": 'irrelevant',
            },
            "vocabulary": {
                "code": region_vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://twitter.com/",
            "percentage": 100,
        }

        res = self.c.post(
                "/api/activities/{}/recipient_regions/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityRecipientRegion.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.region.code, str(data['region']['code']))
        self.assertEqual(instance.percentage, data['percentage'])

    def test_update_recipient_region(self):
        recipient_region = iati_factory.ActivityRecipientRegionFactory.create()
        region = iati_factory.RegionFactory.create(code=89)

        data = {
            "activity": recipient_region.activity.id,
            "region": {
                "code": region.code,
                "name": 'irrelevant',
            },
            "vocabulary": {
                "code": recipient_region.vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://twitter.com/",
            "percentage": 100,
        }

        res = self.c.put(
                "/api/activities/{}/recipient_regions/{}?format=json".format(recipient_region.activity.id, recipient_region.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityRecipientRegion.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.region.code, str(data['region']['code']))
        self.assertEqual(instance.vocabulary.code, str(data['vocabulary']['code']))

    def test_delete_recipient_region(self):
        recipient_region = iati_factory.ActivityRecipientRegionFactory.create()

        res = self.c.delete(
                "/api/activities/{}/recipient_regions/{}?format=json".format(recipient_region.activity.id, recipient_region.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityRecipientRegion.objects.get(pk=recipient_region.id)



class LocationSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_location(self):

        activity = iati_factory.ActivityFactory.create()
        location_reach = iati_factory.GeographicLocationReachFactory.create()
        location_id_vocabulary = iati_factory.GeographicVocabularyFactory.create()
        exactness = iati_factory.GeographicExactnessFactory.create()
        location_class = iati_factory.GeographicLocationClassFactory.create()
        feature_designation = iati_factory.LocationTypeFactory.create()

        type = iati_factory.LocationTypeFactory.create()
        # type = iati_factory.LocationTypeFactory.create(code=2)

        data = {
            "activity": activity.id,
            "ref": "AF-KAN",
            "location_reach": {
                "code": location_reach.code,
                "name": "irrelevant",
            },
            "location_id": {
                "code": "1453782",
                "vocabulary": {
                    "code": location_id_vocabulary.code,
                    "name": "irrelevant"
                },
            },
            "name": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "activity_description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "point": {
                "pos": {
                    "latitude": "31.616944",
                    "longitude": "65.716944",
                },
                "srsName": "http://www.opengis.net/def/crs/EPSG/0/4326",
            },
            "exactness": {
                "code": exactness.code,
                "name": "irrelevant",
            },
            "location_class": {
                "code": location_class.code,
                "name": "irrelevant",
            },
            "feature_designation": {
                "code": feature_designation.code,
                "name": "irrelevant",
            },
        }

        res = self.c.post(
                "/api/activities/{}/locations/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Location.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.location_reach.code, data['location_reach']['code'])
        self.assertEqual(instance.location_id_code, data['location_id']['code'])
        self.assertEqual(instance.location_id_vocabulary.code, data['location_id']['vocabulary']['code'])
        self.assertEqual(instance.exactness.code, data['exactness']['code'])
        self.assertEqual(instance.location_class.code, data['location_class']['code'])
        self.assertEqual(instance.feature_designation.code, data['feature_designation']['code'])

        self.assertEqual(instance.point_srs_name, data['point']['srsName'])
        self.assertEqual(str(instance.point_pos[0]), data['point']['pos']['longitude'])
        self.assertEqual(str(instance.point_pos[1]), data['point']['pos']['latitude'])

        name_narratives = instance.name.narratives.all()
        self.assertEqual(name_narratives[0].content, data['name']['narratives'][0]['text'])
        self.assertEqual(name_narratives[1].content, data['name']['narratives'][1]['text'])

        description_narratives = instance.description.narratives.all()
        self.assertEqual(description_narratives[0].content, data['description']['narratives'][0]['text'])
        self.assertEqual(description_narratives[1].content, data['description']['narratives'][1]['text'])

        activity_description_narratives = instance.activity_description.narratives.all()
        self.assertEqual(activity_description_narratives[0].content, data['activity_description']['narratives'][0]['text'])
        self.assertEqual(activity_description_narratives[1].content, data['activity_description']['narratives'][1]['text'])

    def test_update_location(self):
        location = iati_factory.LocationFactory.create()

        location_reach = iati_factory.GeographicLocationReachFactory.create(code='123')
        location_id_vocabulary = iati_factory.GeographicVocabularyFactory.create(code='A4')
        exactness = iati_factory.GeographicExactnessFactory.create(code=2)
        location_class = iati_factory.GeographicLocationClassFactory.create(code=2)
        feature_designation = iati_factory.LocationTypeFactory.create(code='PPLQ')

        type = iati_factory.LocationTypeFactory.create()
        # type = iati_factory.LocationTypeFactory.create(code=2)

        data = {
            "activity": location.activity.id,
            "ref": "AF-KAN",
            "location_reach": {
                "code": location_reach.code,
                "name": "irrelevant",
            },
            "location_id": {
                "code": "1453782",
                "vocabulary": {
                    "code": location_id_vocabulary.code,
                    "name": "irrelevant"
                },
            },
            "name": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "activity_description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ]
            },
            "point": {
                "pos": {
                    "latitude": "31.616944",
                    "longitude": "65.716944",
                },
                "srsName": "http://www.opengis.net/def/crs/EPSG/0/4326",
            },
            "exactness": {
                "code": exactness.code,
                "name": "irrelevant",
            },
            "location_class": {
                "code": location_class.code,
                "name": "irrelevant",
            },
            "feature_designation": {
                "code": feature_designation.code,
                "name": "irrelevant",
            },
        }

        res = self.c.put(
                "/api/activities/{}/locations/{}?format=json".format(location.activity.id, location.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Location.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.ref, data['ref'])
        self.assertEqual(instance.location_reach.code, data['location_reach']['code'])
        self.assertEqual(instance.location_id_code, data['location_id']['code'])
        self.assertEqual(instance.location_id_vocabulary.code, data['location_id']['vocabulary']['code'])
        self.assertEqual(instance.exactness.code, str(data['exactness']['code']))
        self.assertEqual(instance.location_class.code, data['location_class']['code'])
        self.assertEqual(instance.feature_designation.code, data['feature_designation']['code'])

        self.assertEqual(instance.point_srs_name, data['point']['srsName'])
        self.assertEqual(str(instance.point_pos[0]), data['point']['pos']['longitude'])
        self.assertEqual(str(instance.point_pos[1]), data['point']['pos']['latitude'])

        name_narratives = instance.name.narratives.all()
        self.assertEqual(name_narratives[0].content, data['name']['narratives'][0]['text'])
        self.assertEqual(name_narratives[1].content, data['name']['narratives'][1]['text'])

        description_narratives = instance.description.narratives.all()
        self.assertEqual(description_narratives[0].content, data['description']['narratives'][0]['text'])
        self.assertEqual(description_narratives[1].content, data['description']['narratives'][1]['text'])

        activity_description_narratives = instance.activity_description.narratives.all()
        self.assertEqual(activity_description_narratives[0].content, data['activity_description']['narratives'][0]['text'])
        self.assertEqual(activity_description_narratives[1].content, data['activity_description']['narratives'][1]['text'])




    def test_delete_location(self):
        location = iati_factory.LocationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/locations/{}?format=json".format(location.activity.id, location.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Location.objects.get(pk=location.id)

class HumanitarianScopeSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_humanitarian_scope(self):

        activity = iati_factory.ActivityFactory.create()
        type = iati_factory.HumanitarianScopeTypeFactory.create()
        vocabulary = iati_factory.HumanitarianScopeVocabularyFactory.create()

        data = {
            "activity": activity.id,
            "code": "1",
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "vocabulary": {
                "code": vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://github.com/zimmerman-zimmerman",
        }

        res = self.c.post(
                "/api/activities/{}/humanitarian_scopes/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.HumanitarianScope.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.vocabulary.code, data['vocabulary']['code'])
        self.assertEqual(instance.vocabulary_uri, data['vocabulary_uri'])

    def test_update_humanitarian_scope(self):
        humanitarian_scope = iati_factory.HumanitarianScopeFactory.create()
        type = iati_factory.HumanitarianScopeTypeFactory.create(code="2")
        vocabulary = iati_factory.HumanitarianScopeVocabularyFactory.create(code="2")

        data = {
            "activity": humanitarian_scope.activity.id,
            "code": "1",
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "vocabulary": {
                "code": vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://github.com/zimmerman-zimmerman",
        }

        res = self.c.put(
                "/api/activities/{}/humanitarian_scopes/{}?format=json".format(humanitarian_scope.activity.id, humanitarian_scope.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.HumanitarianScope.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.vocabulary.code, data['vocabulary']['code'])
        self.assertEqual(instance.vocabulary_uri, data['vocabulary_uri'])

    def test_delete_humanitarian_scope(self):
        humanitarian_scopes = iati_factory.HumanitarianScopeFactory.create()

        res = self.c.delete(
                "/api/activities/{}/humanitarian_scopes/{}?format=json".format(humanitarian_scopes.activity.id, humanitarian_scopes.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.HumanitarianScope.objects.get(pk=humanitarian_scopes.id)


class PolicyMarkerSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_policy_marker(self):
        activity = iati_factory.ActivityFactory.create()
        vocabulary = iati_factory.PolicyMarkerVocabularyFactory.create()
        significance = iati_factory.PolicySignificanceFactory.create()
        policy_marker = iati_factory.PolicyMarkerFactory.create()

        data = {
            "activity": activity.id,
            "vocabulary": {
                "code": vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://twitter.com/",
            "policy_marker": {
                "code": policy_marker.code,
                "name": 'irrelevant',
            },
            "significance": {
                "code": significance.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.post(
                "/api/activities/{}/policy_markers/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.ActivityPolicyMarker.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.vocabulary.code, data['vocabulary']['code'])
        self.assertEqual(instance.vocabulary_uri, data['vocabulary_uri'])
        self.assertEqual(instance.code.code, str(data['policy_marker']['code']))
        self.assertEqual(instance.significance.code, str(data['significance']['code']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])

    def test_update_policy_marker(self):
        activity_policy_marker = iati_factory.ActivityPolicyMarkerFactory.create()
        vocabulary = iati_factory.PolicyMarkerVocabularyFactory.create(code=2)
        policy_marker = iati_factory.PolicyMarkerFactory.create(code=2)
        significance = iati_factory.PolicySignificanceFactory.create(code=2)

        data = {
            "activity": activity_policy_marker.activity.id,
            "vocabulary": {
                "code": vocabulary.code,
                "name": 'irrelevant',
            },
            "vocabulary_uri": "https://twitter.com/",
            "policy_marker": {
                "code": policy_marker.code,
                "name": 'irrelevant',
            },
            "significance": {
                "code": significance.code,
                "name": 'irrelevant',
            },
            "narratives": [
                {
                    "text": "test1"
                },
                {
                    "text": "test2"
                }
            ]
        }

        res = self.c.put(
                "/api/activities/{}/policy_markers/{}?format=json".format(activity_policy_marker.activity.id, activity_policy_marker.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.ActivityPolicyMarker.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.vocabulary.code, str(data['vocabulary']['code']))
        self.assertEqual(instance.vocabulary_uri, data['vocabulary_uri'])
        self.assertEqual(instance.code.code, str(data['policy_marker']['code']))
        self.assertEqual(instance.significance.code, str(data['significance']['code']))

        narratives = instance.narratives.all()
        self.assertEqual(narratives[0].content, data['narratives'][0]['text'])
        self.assertEqual(narratives[1].content, data['narratives'][1]['text'])


    def test_delete_policy_marker(self):
        participating_org = iati_factory.ActivityPolicyMarkerFactory.create()

        res = self.c.delete(
                "/api/activities/{}/policy_markers/{}?format=json".format(participating_org.activity.id, participating_org.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityPolicyMarker.objects.get(pk=participating_org.id)


class BudgetSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_budget(self):

        activity = iati_factory.ActivityFactory.create()
        type = iati_factory.BudgetTypeFactory.create()
        status = iati_factory.BudgetStatusFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "activity": activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "period_start": datetime.date.today().isoformat(),
            "period_end": datetime.date.today().isoformat(),
            "value": {
                "value": 123456,
                "currency": {
                    "code": currency.code,
                    "name": 'irrelevant',
                },
                "date": datetime.date.today().isoformat(),
            },
        }

        res = self.c.post(
                "/api/activities/{}/budgets/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Budget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_budget(self):
        budget = iati_factory.BudgetFactory.create()
        type = iati_factory.BudgetTypeFactory.create(code="2")
        status = iati_factory.BudgetStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "activity": budget.activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "period_start": datetime.date.today().isoformat(),
            "period_end": datetime.date.today().isoformat(),
            "value": {
                "value": 123456,
                "currency": {
                    "code": currency.code,
                    "name": 'irrelevant',
                },
                "date": datetime.date.today().isoformat(),
            },
        }

        res = self.c.put(
                "/api/activities/{}/budgets/{}?format=json".format(budget.activity.id, budget.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Budget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_budget(self):
        budgets = iati_factory.BudgetFactory.create()

        res = self.c.delete(
                "/api/activities/{}/budgets/{}?format=json".format(budgets.activity.id, budgets.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Budget.objects.get(pk=budgets.id)

class PlannedDisbursementSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_planned_disbursement(self):

        activity = iati_factory.ActivityFactory.create()
        type = iati_factory.BudgetTypeFactory.create()
        currency = iati_factory.CurrencyFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        organisation_type = iati_factory.OrganisationTypeFactory.create(code=9)
        activity2 = iati_factory.ActivityFactory.create(id="IATI-0002")


        data = {
            "activity": activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "period_start": datetime.date.today().isoformat(),
            "period_end": datetime.date.today().isoformat(),
            "value": {
                "value": 123456,
                "currency": {
                    "code": currency.code,
                    "name": 'irrelevant',
                },
                "date": datetime.date.today().isoformat(),
            },
            "provider_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "receiver_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "receiver_activity": activity2.id,
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
        }

        res = self.c.post(
                "/api/activities/{}/planned_disbursements/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.PlannedDisbursement.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

        instance2 = iati_models.PlannedDisbursementProvider.objects.get(planned_disbursement_id=res.json()['id'])
        self.assertEqual(instance2.ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.normalized_ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.organisation.id, data['provider_organisation']['ref'])
        self.assertEqual(instance2.type.code, str(data['provider_organisation']['type']['code']))
        self.assertEqual(instance2.provider_activity.id, activity.id)

        narratives2 = instance2.narratives.all()
        self.assertEqual(narratives2[0].content, data['provider_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives2[1].content, data['provider_organisation']['narratives'][1]['text'])

        instance3 = iati_models.PlannedDisbursementReceiver.objects.get(planned_disbursement_id=res.json()['id'])
        self.assertEqual(instance3.ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.normalized_ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.organisation.id, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.type.code, str(data['receiver_organisation']['type']['code']))
        self.assertEqual(instance3.receiver_activity.id, data['receiver_organisation']['receiver_activity'])

        narratives3 = instance3.narratives.all()
        self.assertEqual(narratives3[0].content, data['receiver_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives3[1].content, data['receiver_organisation']['narratives'][1]['text'])


    def test_update_planned_disbursement(self):
        planned_disbursement = iati_factory.PlannedDisbursementFactory.create()
        type = iati_factory.PlannedDisbursementTypeFactory.create(code="2")
        status = iati_factory.PlannedDisbursementStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "activity": planned_disbursement.activity.id,
            "type": {
                "code": type.code,
                "name": 'irrelevant',
            },
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "period_start": datetime.date.today().isoformat(),
            "period_end": datetime.date.today().isoformat(),
            "value": {
                "value": 123456,
                "currency": {
                    "code": currency.code,
                    "name": 'irrelevant',
                },
                "date": datetime.date.today().isoformat(),
            },
        }

        res = self.c.put(
                "/api/activities/{}/planned_disbursements/{}?format=json".format(planned_disbursement.activity.id, planned_disbursement.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.PlannedDisbursement.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, data['type']['code'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_planned_disbursement(self):
        planned_disbursements = iati_factory.PlannedDisbursementFactory.create()

        res = self.c.delete(
                "/api/activities/{}/planned_disbursements/{}?format=json".format(planned_disbursements.activity.id, planned_disbursements.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.PlannedDisbursement.objects.get(pk=planned_disbursements.id)



class TransactionSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_transaction(self):
        activity = iati_factory.ActivityFactory.create()
        transaction_type = iati_factory.TransactionTypeFactory.create()
        currency = iati_factory.CurrencyFactory.create()
        organisation_type = iati_factory.OrganisationTypeFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        activity2 = iati_factory.ActivityFactory.create(id="IATI-0002")
        # sector = iati_factory.SectorFactory.create()
        # sector_vocabulary = iati_factory.SectorVocabulary.create()
        # recipient_country = transaction_factory.TransactionRecipientCountryFactory.create()
        # recipient_region = transaction_factory.TransactionRecipientRegionFactory.create()
        country = iati_factory.CountryFactory.create()
        region = iati_factory.RegionFactory.create()
        region_vocabulary = iati_factory.RegionVocabularyFactory.create()
        disbursement_channel = iati_factory.DisbursementChannelFactory.create()
        flow_type = iati_factory.FlowTypeFactory.create()
        finance_type = iati_factory.FinanceTypeFactory.create()
        aid_type = iati_factory.AidTypeFactory.create()
        tied_status = iati_factory.TiedStatusFactory.create()

        data = {
            "activity_id": activity.id,
            "ref": "test-ref",
            "humanitarian": 1,
            "transaction_type": {
                "code": transaction_type.code,
                "name": 'irrelevant',
            },
            "transaction_date": datetime.date.today().isoformat(),
            "value": 123456,
            "value_date": datetime.date.today().isoformat(),
            "currency": {
                "code": currency.code,
                "name": 'irrelevant',
            },
            "date": datetime.date.today().isoformat(),
            "description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "provider_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "receiver_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "receiver_activity_id": activity2.id,
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "disbursement_channel": {
                "code": disbursement_channel.code,
                "name": 'irrelevant',
            },
            "transaction_type": {
                "code": transaction_type.code,
                "name": 'irrelevant',
            },
            "recipient_country": {
                "country": {
                    "code": country.code,
                    "name": 'irrelevant',
                },
            },
            "recipient_region": {
                "region": {
                    "code": region.code,
                    "name": 'irrelevant',
                },
                "vocabulary": {
                    "code": region_vocabulary.code,
                    "name": 'irrelevant',
                },
                "vocabulary_uri": "https://twitter.com/",
            },
            # "sector": {
            #     "sector": {
            #         "code": sector.code,
            #         "name": 'irrelevant',
            #     },
            #     "vocabulary": {
            #         "code": sector_vocabulary.code,
            #         "name": 'irrelevant',
            #     },
            #     "vocabulary_uri": "https://twitter.com/",
            # },
            "flow_type": {
                "code": flow_type.code,
                "name": 'irrelevant',
            },
            "finance_type": {
                "code": finance_type.code,
                "name": 'irrelevant',
            },
            "aid_type": {
                "code": aid_type.code,
                "name": 'irrelevant',
            },
            "tied_status": {
                "code": tied_status.code,
                "name": 'irrelevant',
            },
        }

        res = self.c.post(
                "/api/activities/{}/transactions/?format=json".format(activity.id), 
                data,
                format='json'
                )

        result = res.json()

        self.assertEquals(res.status_code, 201, result)

        instance = transaction_models.Transaction.objects.get(pk=result['id'])

        self.assertEqual(instance.activity.id, data['activity_id'])
        self.assertEqual(instance.finance_type.code, data['finance_type']['code'])
        self.assertEqual(instance.transaction_date.isoformat(), data['transaction_date'])
        self.assertEqual(instance.value, data['value'])
        self.assertEqual(instance.currency.code, data['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['date'])
        self.assertEqual(instance.flow_type.code, str(data['flow_type']['code']))
        self.assertEqual(instance.finance_type.code, str(data['finance_type']['code']))
        self.assertEqual(instance.aid_type.code, str(data['aid_type']['code']))
        self.assertEqual(instance.tied_status.code, str(data['tied_status']['code']))

        instance2 = transaction_models.TransactionProvider.objects.get(transaction_id=result['id'])
        self.assertEqual(instance2.ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.normalized_ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.organisation.id, data['provider_organisation']['ref'])
        self.assertEqual(instance2.type.code, str(data['provider_organisation']['type']['code']))
        self.assertEqual(instance2.provider_activity.id, activity.id)

        narratives2 = instance2.narratives.all()
        self.assertEqual(narratives2[0].content, data['provider_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives2[1].content, data['provider_organisation']['narratives'][1]['text'])

        instance3 = transaction_models.TransactionReceiver.objects.get(transaction_id=result['id'])
        self.assertEqual(instance3.ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.normalized_ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.organisation.id, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.type.code, str(data['receiver_organisation']['type']['code']))
        self.assertEqual(instance3.receiver_activity.id, data['receiver_organisation']['receiver_activity_id'])

        narratives3 = instance3.narratives.all()
        self.assertEqual(narratives3[0].content, data['receiver_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives3[1].content, data['receiver_organisation']['narratives'][1]['text'])

        # transaction_sector = iati_models.TransactionSector.objects.filter(transaction_id=result['id'])[0]


    def test_update_transaction(self):
        transaction = transaction_factory.TransactionFactory.create()
        transaction_type = iati_factory.TransactionTypeFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code="af")
        organisation_type = iati_factory.OrganisationTypeFactory.create()
        organisation = iati_factory.OrganisationFactory.create()
        activity2 = iati_factory.ActivityFactory.create(id="IATI-0002")
        # sector = iati_factory.SectorFactory.create()
        # sector_vocabulary = iati_factory.SectorVocabulary.create()
        # recipient_country = transaction_factory.TransactionRecipientCountryFactory.create()
        # recipient_region = transaction_factory.TransactionRecipientRegionFactory.create()
        country = iati_factory.CountryFactory.create()
        region = iati_factory.RegionFactory.create()
        region_vocabulary = iati_factory.RegionVocabularyFactory.create()
        disbursement_channel = iati_factory.DisbursementChannelFactory.create()
        flow_type = iati_factory.FlowTypeFactory.create()
        finance_type = iati_factory.FinanceTypeFactory.create()
        aid_type = iati_factory.AidTypeFactory.create()
        tied_status = iati_factory.TiedStatusFactory.create()

        data = {
            "activity_id": transaction.activity.id,
            "ref": "test-ref",
            "humanitarian": 1,
            "transaction_type": {
                "code": transaction_type.code,
                "name": 'irrelevant',
            },
            "transaction_date": datetime.date.today().isoformat(),
            "value": 123456,
            "value_date": datetime.date.today().isoformat(),
            "currency": {
                "code": currency.code,
                "name": 'irrelevant',
            },
            "date": datetime.date.today().isoformat(),
            "description": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "provider_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "receiver_organisation": {
                "ref": organisation.id,
                "type": {
                    "code": organisation_type.code,
                    "name": 'irrelevant',
                },
                "receiver_activity_id": activity2.id,
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "disbursement_channel": {
                "code": disbursement_channel.code,
                "name": 'irrelevant',
            },
            "transaction_type": {
                "code": transaction_type.code,
                "name": 'irrelevant',
            },
            "recipient_country": {
                "country": {
                    "code": country.code,
                    "name": 'irrelevant',
                },
            },
            "recipient_region": {
                "region": {
                    "code": region.code,
                    "name": 'irrelevant',
                },
                "vocabulary": {
                    "code": region_vocabulary.code,
                    "name": 'irrelevant',
                },
                "vocabulary_uri": "https://twitter.com/",
            },
            # "sector": {
            #     "sector": {
            #         "code": sector.code,
            #         "name": 'irrelevant',
            #     },
            #     "vocabulary": {
            #         "code": sector_vocabulary.code,
            #         "name": 'irrelevant',
            #     },
            #     "vocabulary_uri": "https://twitter.com/",
            # },
            "flow_type": {
                "code": flow_type.code,
                "name": 'irrelevant',
            },
            "finance_type": {
                "code": finance_type.code,
                "name": 'irrelevant',
            },
            "aid_type": {
                "code": aid_type.code,
                "name": 'irrelevant',
            },
            "tied_status": {
                "code": tied_status.code,
                "name": 'irrelevant',
            },
        }


        res = self.c.put(
                "/api/activities/{}/transactions/{}?format=json".format(transaction.activity.id, transaction.id), 
                data,
                format='json'
                )


        self.assertEquals(res.status_code, 200, res.json())
        result = res.json()

        instance = transaction_models.Transaction.objects.get(pk=result['id'])

        self.assertEqual(instance.activity.id, data['activity_id'])
        self.assertEqual(instance.finance_type.code, data['finance_type']['code'])
        self.assertEqual(instance.transaction_date.isoformat(), data['transaction_date'])
        self.assertEqual(instance.value, data['value'])
        self.assertEqual(instance.currency.code, data['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['date'])
        self.assertEqual(instance.flow_type.code, str(data['flow_type']['code']))
        self.assertEqual(instance.finance_type.code, str(data['finance_type']['code']))
        self.assertEqual(instance.aid_type.code, str(data['aid_type']['code']))
        self.assertEqual(instance.tied_status.code, str(data['tied_status']['code']))

        instance2 = transaction_models.TransactionProvider.objects.get(transaction_id=result['id'])
        self.assertEqual(instance2.ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.normalized_ref, data['provider_organisation']['ref'])
        self.assertEqual(instance2.organisation.id, data['provider_organisation']['ref'])
        self.assertEqual(instance2.type.code, str(data['provider_organisation']['type']['code']))
        self.assertEqual(instance2.provider_activity.id, activity.id)

        narratives2 = instance2.narratives.all()
        self.assertEqual(narratives2[0].content, data['provider_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives2[1].content, data['provider_organisation']['narratives'][1]['text'])

        instance3 = transaction_models.TransactionReceiver.objects.get(transaction_id=result['id'])
        self.assertEqual(instance3.ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.normalized_ref, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.organisation.id, data['receiver_organisation']['ref'])
        self.assertEqual(instance3.type.code, str(data['receiver_organisation']['type']['code']))
        self.assertEqual(instance3.receiver_activity.id, data['receiver_organisation']['receiver_activity_id'])

        narratives3 = instance3.narratives.all()
        self.assertEqual(narratives3[0].content, data['receiver_organisation']['narratives'][0]['text'])
        self.assertEqual(narratives3[1].content, data['receiver_organisation']['narratives'][1]['text'])

        # transaction_sector = iati_models.TransactionSector.objects.filter(transaction_id=result['id'])[0]



    def test_delete_transaction(self):
        transactions = iati_factory.TransactionFactory.create()

        res = self.c.delete(
                "/api/activities/{}/transactions/{}?format=json".format(transactions.activity.id, transactions.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Transaction.objects.get(pk=transactions.id)

