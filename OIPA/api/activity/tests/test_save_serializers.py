
# TODO: no need to test codelist fields separately; instead test the whole serializer in once along with the code and vocabulary fields. Or is testing the fields separately preferable?

from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
import datetime

from django.test import RequestFactory, Client
from rest_framework.test import APIClient
from iati.factory import iati_factory
from iati_codelists.factory import codelist_factory
from api.activity import serializers
from iati import models as iati_models
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
            "xml_source_ref": "test", # TODO: temporarily, until we separate drafts - 2016-10-03
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
            "xml_source_ref": "test", # TODO: temporarily, until we separate drafts - 2016-10-03
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


    def test_delete_reporting_organisation(self):
        reporting_org = iati_factory.ReportingOrganisationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/reporting_organisations/{}?format=json".format(reporting_org.activity.id, reporting_org.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityReportingOrganisation.objects.get(ref=reporting_org.ref)

class TitleSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def test_create_title(self):

        activity = iati_factory.ActivityFactory.create()

        data = {
            "activity": activity.id,
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
                "/api/activities/{}/titles/?format=json".format(activity.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Title.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])

        narratives = instance.narratives()
        self.assertEqual(narratives[0].content, data['narratives'][0])
        self.assertEqual(narratives[1].content, data['narratives'][1])


        instance = iati_models.Title.objects.get(pk=res.json()['id'])
        # self.assertEqual(instance.type.code, data['type']['code'])

    def test_update_title(self):
        title = iati_factory.TitleFactory.create()

        data = {
            "activity": title.activity.id,
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
                "/api/activities/{}/titles/{}?format=json".format(title.activity.id, title.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Title.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])

        narratives = instance.narratives()
        self.assertEqual(narratives[0].content, data['narratives'][0])
        self.assertEqual(narratives[1].content, data['narratives'][1])


    def test_delete_title(self):
        title = iati_factory.TitleFactory.create()

        res = self.c.delete(
                "/api/activities/{}/titles/{}?format=json".format(title.activity.id, title.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Title.objects.get(pk=title.id)



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
                    "text": "text123"
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
                    "text": "text123"
                }
            ]
        }

        print("/api/activities/{}/descriptions/{}?format=json".format(description.activity.id, description.id))
        res = self.c.put(
                "/api/activities/{}/descriptions/{}?format=json".format(description.activity.id, description.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Description.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.activity.id, data['activity'])
        self.assertEqual(instance.type.code, str(data['type']['code']))


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


    def test_delete_participating_organisation(self):
        participating_org = iati_factory.ParticipatingOrganisationFactory.create()

        res = self.c.delete(
                "/api/activities/{}/participating_organisations/{}?format=json".format(participating_org.activity.id, participating_org.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.ActivityParticipatingOrganisation.objects.get(pk=participating_org.id)
