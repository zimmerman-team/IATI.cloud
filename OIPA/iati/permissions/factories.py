import datetime
import md5


from iati.permissions.models import AdminGroup
from django.contrib.auth.models import User

from factory.django import DjangoModelFactory
import factory
from factory import SubFactory, RelatedFactory

from iati_synchroniser.factory import synchroniser_factory

class UserFactory(DjangoModelFactory):
    username = 'john'

    class Meta:
        model = User  # Equivalent to ``model = myapp.models.User``
        django_get_or_create = ('username',)

class AdminGroupFactory(DjangoModelFactory):
    name = "DFID Admin Group"
    publisher = SubFactory(synchroniser_factory.PublisherFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = AdminGroup

