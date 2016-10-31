from django.db import models
from django.contrib.auth.models import Group, User, AbstractUser

from iati_synchroniser.models import Publisher

class OrganisationUser(AbstractUser):
    # the IR API key
    iati_api_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Organisation users"


class OrganisationAdminGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.ForeignKey(Publisher, unique=True)
    owner = models.ForeignKey(OrganisationUser)

    class Meta:
        verbose_name_plural = "Organisation admin groups"
        ordering = ['name']


# TODO: when are these created? - 2016-10-24
class OrganisationGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.ForeignKey(Publisher, unique=True)

    # TODO: is this nescessary? - 2016-10-24
    # owner = models.ForeignKey(User)

    class Meta:
        verbose_name_plural = "Organisation groups"
        ordering = ['name']


