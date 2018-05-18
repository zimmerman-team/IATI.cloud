import datetime

from django.contrib.auth.models import User
from iati.permissions.models import OrganisationAdminGroup, OrganisationGroup
from iati.permissions.models import OrganisationUser

from factory.django import DjangoModelFactory
import factory
from factory import SubFactory, RelatedFactory

from iati_synchroniser.factory import synchroniser_factory


class OrganisationUserFactory(DjangoModelFactory):
    user = SubFactory('iati.permissions.factories.UserFactory', organisationuser=None)

    class Meta:
        model = OrganisationUser  # Equivalent to ``model = myapp.models.User``
        # django_get_or_create = ('user.username',)


class UserFactory(DjangoModelFactory):
    username = 'john'
    organisationuser = RelatedFactory(OrganisationUserFactory, 'user')

    class Meta:
        model = User  # Equivalent to ``model = myapp.models.User``
        django_get_or_create = ('username',)


class OrganisationAdminGroupFactory(DjangoModelFactory):
    name = "DFID Organisation Admin Group"
    publisher = SubFactory(synchroniser_factory.PublisherFactory)
    owner = SubFactory(OrganisationUserFactory)

    class Meta:
        model = OrganisationAdminGroup


class OrganisationGroupFactory(DjangoModelFactory):
    name = "DFID Organisation Organisation Group"
    publisher = SubFactory(synchroniser_factory.PublisherFactory)

    class Meta:
        model = OrganisationGroup
