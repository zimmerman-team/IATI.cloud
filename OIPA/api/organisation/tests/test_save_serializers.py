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
from iati_organisation import models as org_models
from iati.transaction import models as transaction_models
from django.core.exceptions import ObjectDoesNotExist
from iati.permissions.factories import OrganisationAdminGroupFactory, OrganisationUserFactory
from rest_framework.exceptions import ValidationError

from decimal import Decimal

from iati.parser.exceptions import *


class OrganisationSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_organisation(self):

        iati_version = codelist_factory.VersionFactory.create(code="2.02")
        language = codelist_factory.LanguageFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation_identifier": 'bladiebloebla',
            "xml_lang": language.code,
            'default_currency': {
                "code": currency.code,
                "name": 'irrelevant',
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
            "capital_spend": Decimal("20.2")
        }

        res = self.c.post(
                "/api/publishers/{}/organisations/?format=json".format(self.publisher.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = iati_models.Organisation.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation_identifier, data['organisation_identifier'])
        self.assertEqual(instance.iati_standard_version.code, "2.02")
        self.assertEqual(instance.default_currency.code, currency.code)

        name = instance.name
        name_narratives = name.narratives.all()
        self.assertEqual(name_narratives[0].content, data['name']['narratives'][0]['text'])
        self.assertEqual(name_narratives[1].content, data['name']['narratives'][1]['text'])

    def test_update_organisation(self):
        organisation = iati_factory.OrganisationFactory.create()
        title = iati_factory.OrganisationNameFactory.create(organisation=organisation)

        language = codelist_factory.LanguageFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "id": organisation.id,
            "organisation_identifier": 'bladiebloebla',
            "xml_lang": language.code,
            'default_currency': {
                "code": currency.code,
                "name": 'irrelevant',
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
            "capital_spend": Decimal("20.2")
        }

        res = self.c.put(
                "/api/publishers/{}/organisations/{}/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = iati_models.Organisation.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation_identifier, data['organisation_identifier'])
        self.assertEqual(instance.iati_standard_version.code, "2.02")
        self.assertEqual(instance.default_currency.code, currency.code)

        name = instance.name
        name_narratives = name.narratives.all()
        self.assertEqual(name_narratives[0].content, data['name']['narratives'][0]['text'])
        self.assertEqual(name_narratives[1].content, data['name']['narratives'][1]['text'])

    def test_delete_organisation(self):
        organisation = iati_factory.OrganisationFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/?format=json".format(self.publisher.id, organisation.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = iati_models.Organisation.objects.get(pk=organisation.id)

class OrganisationTotalBudgetSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_total_budget(self):

        organisation = iati_factory.OrganisationFactory.create()
        status = iati_factory.BudgetStatusFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation": organisation.id,
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
                "/api/publishers/{}/organisations/{}/total_budgets/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.TotalBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_total_budgets(self):
        total_budget = iati_factory.OrganisationTotalBudgetFactory.create()
        status = iati_factory.BudgetStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "organisation": total_budget.organisation.id,
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
                "/api/publishers/{}/organisations/{}/total_budgets/{}?format=json".format(self.publisher.id, total_budget.organisation.id, total_budget.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.TotalBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_budget(self):
        total_budget = iati_factory.OrganisationTotalBudgetFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/total_budgets/{}?format=json".format(self.publisher.id, total_budget.organisation.id, total_budget.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.TotalBudget.objects.get(pk=total_budget.id)

class OrganisationRecipientOrgBudgetSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_recipient_org_budget(self):

        organisation = iati_factory.OrganisationFactory.create()
        recipient_org = iati_factory.OrganisationFactory.create(organisation_identifier="org-2")
        status = iati_factory.BudgetStatusFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation": organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_org": {
                "ref": recipient_org.organisation_identifier
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
                "/api/publishers/{}/organisations/{}/recipient_org_budgets/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.RecipientOrgBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.recipient_org_identifier, data['recipient_org']['ref'])
        self.assertEqual(instance.recipient_org.organisation_identifier, data['recipient_org']['ref'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_recipient_org_budgets(self):
        recipient_org_budget = iati_factory.OrganisationRecipientOrgBudgetFactory.create()
        recipient_org = iati_factory.OrganisationFactory.create(organisation_identifier="org-2")
        status = iati_factory.BudgetStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "organisation": recipient_org_budget.organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_org": {
                "ref": recipient_org.organisation_identifier
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
                "/api/publishers/{}/organisations/{}/recipient_org_budgets/{}?format=json".format(self.publisher.id, recipient_org_budget.organisation.id, recipient_org_budget.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.RecipientOrgBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.recipient_org_identifier, data['recipient_org']['ref'])
        self.assertEqual(instance.recipient_org.organisation_identifier, data['recipient_org']['ref'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_recipient_org_budget(self):
        recipient_org_budget = iati_factory.OrganisationRecipientOrgBudgetFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/recipient_org_budgets/{}?format=json".format(self.publisher.id, recipient_org_budget.organisation.id, recipient_org_budget.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.RecipientOrgBudget.objects.get(pk=recipient_org_budget.id)

