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


class OrganisationRecipientCountryBudgetSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_recipient_country_budget(self):

        organisation = iati_factory.OrganisationFactory.create()
        country = iati_factory.CountryFactory.create()
        status = iati_factory.BudgetStatusFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation": organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_country": {
                "code": country.code,
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
                "/api/publishers/{}/organisations/{}/recipient_country_budgets/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.RecipientCountryBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.country.code, data['recipient_country']['code'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_recipient_country_budgets(self):
        recipient_country_budget = iati_factory.OrganisationRecipientCountryBudgetFactory.create()
        country = iati_factory.CountryFactory.create()
        status = iati_factory.BudgetStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "organisation": recipient_country_budget.organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_country": {
                "code": country.code,
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
                "/api/publishers/{}/organisations/{}/recipient_country_budgets/{}?format=json".format(self.publisher.id, recipient_country_budget.organisation.id, recipient_country_budget.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.RecipientCountryBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.country.code, data['recipient_country']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_recipient_country_budget(self):
        recipient_country_budget = iati_factory.OrganisationRecipientCountryBudgetFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/recipient_country_budgets/{}?format=json".format(self.publisher.id, recipient_country_budget.organisation.id, recipient_country_budget.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.RecipientCountryBudget.objects.get(pk=recipient_country_budget.id)

class OrganisationRecipientRegionBudgetSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_recipient_region_budget(self):

        organisation = iati_factory.OrganisationFactory.create()
        region = iati_factory.RegionFactory.create()
        status = iati_factory.BudgetStatusFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation": organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_region": {
                "code": region.code,
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
                "/api/publishers/{}/organisations/{}/recipient_region_budgets/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.RecipientRegionBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.region.code, data['recipient_region']['code'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_recipient_region_budgets(self):
        recipient_region_budget = iati_factory.OrganisationRecipientRegionBudgetFactory.create()
        region = iati_factory.RegionFactory.create()
        status = iati_factory.BudgetStatusFactory.create(code="2")
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "organisation": recipient_region_budget.organisation.id,
            "status": {
                "code": status.code,
                "name": 'irrelevant',
            },
            "recipient_region": {
                "code": region.code,
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
                "/api/publishers/{}/organisations/{}/recipient_region_budgets/{}?format=json".format(self.publisher.id, recipient_region_budget.organisation.id, recipient_region_budget.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.RecipientRegionBudget.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.status.code, data['status']['code'])
        self.assertEqual(instance.region.code, data['recipient_region']['code'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_recipient_region_budget(self):
        recipient_region_budget = iati_factory.OrganisationRecipientRegionBudgetFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/recipient_region_budgets/{}?format=json".format(self.publisher.id, recipient_region_budget.organisation.id, recipient_region_budget.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.RecipientRegionBudget.objects.get(pk=recipient_region_budget.id)

class OrganisationTotalExpenditureSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_total_expenditure(self):

        organisation = iati_factory.OrganisationFactory.create()
        currency = iati_factory.CurrencyFactory.create()

        data = {
            "organisation": organisation.id,
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
                "/api/publishers/{}/organisations/{}/total_expenditures/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.TotalExpenditure.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_update_total_expenditures(self):
        total_expenditure = iati_factory.OrganisationTotalExpenditureFactory.create()
        currency = iati_factory.CurrencyFactory.create(code='af')

        data = {
            "organisation": total_expenditure.organisation.id,
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
                "/api/publishers/{}/organisations/{}/total_expenditures/{}?format=json".format(self.publisher.id, total_expenditure.organisation.id, total_expenditure.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.TotalExpenditure.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.period_start.isoformat(), data['period_start'])
        self.assertEqual(instance.period_end.isoformat(), data['period_end'])
        self.assertEqual(instance.value, data['value']['value'])
        self.assertEqual(instance.currency.code, data['value']['currency']['code'])
        self.assertEqual(instance.value_date.isoformat(), data['value']['date'])

    def test_delete_total_expenditure(self):
        total_expenditure = iati_factory.OrganisationTotalExpenditureFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/total_expenditures/{}?format=json".format(self.publisher.id, total_expenditure.organisation.id, total_expenditure.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.TotalExpenditure.objects.get(pk=total_expenditure.id)




class DocumentLinkSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_document_link(self):
        organisation = iati_factory.OrganisationFactory.create()
        file_format = codelist_factory.FileFormatFactory.create()

        data = {
            "organisation": organisation.id,
            "url": "https://bitcoin.org/bitcoin.pdf",
            "title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "document_date": {
                "iso_date": datetime.date.today().isoformat(),
            },
            "format": {
                "code": file_format.code,
                "name": "random_stuff",
            }
        }

        res = self.c.post(
                "/api/publishers/{}/organisations/{}/document_links/?format=json".format(self.publisher.id, organisation.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.OrganisationDocumentLink.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.url, data['url'])
        self.assertEqual(instance.iso_date.isoformat(), data['document_date']['iso_date'])
        self.assertEqual(instance.file_format.code, data['format']['code'])

        instance2 = org_models.DocumentLinkTitle.objects.get(document_link_id=res.json()['id'])
        narratives2 = instance2.narratives.all()
        self.assertEqual(narratives2[0].content, data['title']['narratives'][0]['text'])
        self.assertEqual(narratives2[1].content, data['title']['narratives'][1]['text'])

    def test_update_document_link(self):
        document_link = iati_factory.OrganisationDocumentLinkFactory.create()
        file_format = codelist_factory.FileFormatFactory.create(code="application/json")

        data = {
            "organisation": document_link.organisation.id,
            "url": "https://bitcoin.org/bitcoin.pdf",
            "title": {
                "narratives": [
                    {
                        "text": "test1"
                    },
                    {
                        "text": "test2"
                    }
                ],
            },
            "document_date": {
                "iso_date": datetime.date.today().isoformat(),
            },
            "format": {
                "code": file_format.code,
                "name": "random_stuff",
            }
        }

        res = self.c.put(
                "/api/publishers/{}/organisations/{}/document_links/{}?format=json".format(self.publisher.id, document_link.organisation.id, document_link.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.OrganisationDocumentLink.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.organisation.id, data['organisation'])
        self.assertEqual(instance.url, data['url'])
        self.assertEqual(instance.iso_date.isoformat(), data['document_date']['iso_date'])
        self.assertEqual(instance.file_format.code, data['format']['code'])

        instance2 = org_models.DocumentLinkTitle.objects.get(document_link_id=res.json()['id'])
        narratives2 = instance2.narratives.all()
        self.assertEqual(narratives2[0].content, data['title']['narratives'][0]['text'])
        self.assertEqual(narratives2[1].content, data['title']['narratives'][1]['text'])

    def test_delete_document_link(self):
        document_links = iati_factory.OrganisationDocumentLinkFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/document_links/{}?format=json".format(self.publisher.id, document_links.organisation.id, document_links.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.OrganisationDocumentLink.objects.get(pk=document_links.id)


class DocumentLinkCategorySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_document_link_category(self):
        document_link = iati_factory.OrganisationDocumentLinkFactory.create()
        document_category = codelist_factory.DocumentCategoryFactory.create()

        data = {
            "document_link": document_link.id,
            "category": {
                "code": document_category.code,
                "name": "random_stuff",
            }
        }

        res = self.c.post(
                "/api/publishers/{}/organisations/{}/document_links/{}/categories/?format=json".format(self.publisher.id, document_link.organisation.id, document_link.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.OrganisationDocumentLinkCategory.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.category.code, data['category']['code'])

    def test_update_document_link_category(self):
        document_link_category = iati_factory.OrganisationDocumentLinkCategoryFactory.create()
        document_category = codelist_factory.DocumentCategoryFactory.create(code="2")

        data = {
            "document_link": document_link_category.document_link.id,
            "category": {
                "code": document_category.code,
                "name": "random_stuff",
            }
        }

        res = self.c.put(
                "/api/publishers/{}/organisations/{}/document_links/{}/categories/{}?format=json".format(self.publisher.id, document_link_category.document_link.organisation.id, document_link_category.document_link.id, document_link_category.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.OrganisationDocumentLinkCategory.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.category.code, data['category']['code'])

    def test_delete_document_link_category(self):
        document_link_category = iati_factory.OrganisationDocumentLinkCategoryFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/document_links/{}/categories/{}?format=json".format(self.publisher.id, document_link_category.document_link.organisation.id, document_link_category.document_link.id, document_link_category.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.OrganisationDocumentLinkCategory.objects.get(pk=document_link_category.id)


class DocumentLinkLanguageSaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_language(self):
        document_link = iati_factory.OrganisationDocumentLinkFactory.create()
        language = codelist_factory.LanguageFactory.create()

        data = {
            "document_link": document_link.id,
            "language": {
                "code": language.code,
                "name": "random_stuff",
            }
        }

        res = self.c.post(
                "/api/publishers/{}/organisations/{}/document_links/{}/languages/?format=json".format(self.publisher.id, document_link.organisation.id, document_link.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.OrganisationDocumentLinkLanguage.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.language.code, data['language']['code'])

    def test_update_language(self):
        document_link_language = iati_factory.OrganisationDocumentLinkLanguageFactory.create()
        language = codelist_factory.LanguageFactory.create(code="2")

        data = {
            "document_link": document_link_language.document_link.id,
            "language": {
                "code": language.code,
                "name": "random_stuff",
            }
        }

        res = self.c.put(
                "/api/publishers/{}/organisations/{}/document_links/{}/languages/{}?format=json".format(self.publisher.id, document_link_language.document_link.organisation.id, document_link_language.document_link.id, document_link_language.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.OrganisationDocumentLinkLanguage.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.language.code, data['language']['code'])

    def test_delete_language(self):
        document_link_language = iati_factory.OrganisationDocumentLinkLanguageFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/document_links/{}/languages/{}?format=json".format(self.publisher.id, document_link_language.document_link.organisation.id, document_link_language.document_link.id, document_link_language.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.OrganisationDocumentLinkLanguage.objects.get(pk=document_link_language.id)



class DocumentLinkRecipientCountrySaveTestCase(TestCase):
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    def setUp(self):
        admin_group = OrganisationAdminGroupFactory.create()
        user = OrganisationUserFactory.create(user__username='test1')

        admin_group.organisationuser_set.add(user)

        self.publisher = admin_group.publisher

        self.c.force_authenticate(user.user)

    def test_create_recipient_country(self):
        document_link = iati_factory.OrganisationDocumentLinkFactory.create()
        recipient_country = iati_factory.CountryFactory.create()

        data = {
            "document_link": document_link.id,
            "recipient_country": {
                "code": recipient_country.code,
                "name": "random_stuff",
            }
        }

        res = self.c.post(
                "/api/publishers/{}/organisations/{}/document_links/{}/recipient_countries/?format=json".format(self.publisher.id, document_link.organisation.id, document_link.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 201, res.json())

        instance = org_models.DocumentLinkRecipientCountry.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.recipient_country.code, data['recipient_country']['code'])

    def test_update_recipient_country(self):
        document_link_recipient_country = iati_factory.OrganisationDocumentLinkRecipientCountryFactory.create()
        recipient_country = iati_factory.CountryFactory.create(code="2")

        data = {
            "document_link": document_link_recipient_country.document_link.id,
            "recipient_country": {
                "code": recipient_country.code,
                "name": "random_stuff",
            }
        }

        res = self.c.put(
                "/api/publishers/{}/organisations/{}/document_links/{}/recipient_countries/{}?format=json".format(self.publisher.id, document_link_recipient_country.document_link.organisation.id, document_link_recipient_country.document_link.id, document_link_recipient_country.id), 
                data,
                format='json'
                )

        self.assertEquals(res.status_code, 200, res.json())

        instance = org_models.DocumentLinkRecipientCountry.objects.get(pk=res.json()['id'])

        self.assertEqual(instance.document_link.id, data['document_link'])
        self.assertEqual(instance.recipient_country.code, data['recipient_country']['code'])

    def test_delete_recipient_country(self):
        document_link_recipient_country = iati_factory.OrganisationDocumentLinkRecipientCountryFactory.create()

        res = self.c.delete(
                "/api/publishers/{}/organisations/{}/document_links/{}/recipient_countries/{}?format=json".format(self.publisher.id, document_link_recipient_country.document_link.organisation.id, document_link_recipient_country.document_link.id, document_link_recipient_country.id), 
                format='json'
                )

        self.assertEquals(res.status_code, 204)

        with self.assertRaises(ObjectDoesNotExist):
            instance = org_models.DocumentLinkRecipientCountry.objects.get(pk=document_link_recipient_country.id)
