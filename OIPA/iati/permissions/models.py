from django.db import models
from django.contrib.auth.models import Group, User, AbstractUser

from iati_synchroniser.models import Publisher

class OrganisationUser(models.Model):

    # the IR API key
    iati_api_key = models.CharField(max_length=255, null=True, blank=True)

    user = models.ForeignKey(User)

    organisation_admin_groups = models.ManyToManyField(
        'OrganisationAdminGroup',
        verbose_name='Organisation Admin Groups',
        blank=True,
        # help_text=_(
        #     'The groups this user belongs to. A user will get all permissions '
        #     'granted to each of their groups.'
        # ),
        related_name="organisationuser_set",
        # related_query_name="user",
    )

    organisation_groups = models.ManyToManyField(
        'OrganisationGroup',
        verbose_name='Organisation Groups',
        blank=True,
        # help_text=_(
        #     'The groups this user belongs to. A user will get all permissions '
        #     'granted to each of their groups.'
        # ),
        related_name="organisationuser_set",
        # related_query_name="user",
    )

    class Meta:
        verbose_name_plural = "Organisation users"
        # db_table = 'auth_user'


class OrganisationAdminGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.ForeignKey(Publisher, unique=True)
    owner = models.ForeignKey(OrganisationUser, null=True)

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

