from django.contrib.auth.models import Group, User
from django.db import models

from iati_synchroniser.models import Publisher


class OrganisationUser(models.Model):

    # the IR API key
    iati_api_key = models.CharField(max_length=255, null=True, blank=True)
    iati_user_id = models.CharField(max_length=255, null=True, blank=True)

    user = models.OneToOneField(
        User, related_name='organisationuser', on_delete=models.CASCADE)

    organisation_admin_groups = models.ManyToManyField(
        'OrganisationAdminGroup',
        verbose_name='Organisation Admin Groups',
        blank=True,
        related_name="organisationuser_set",
    )

    organisation_groups = models.ManyToManyField(
        'OrganisationGroup',
        verbose_name='Organisation Groups',
        blank=True,
        related_name="organisationuser_set",
    )

    class Meta:
        verbose_name_plural = "Organisation users"


class OrganisationAdminGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.OneToOneField(Publisher, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        OrganisationUser, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Organisation admin groups"
        ordering = ['name']


# TODO: when are these created? - 2016-10-24
class OrganisationGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.OneToOneField(Publisher, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Organisation groups"
        ordering = ['name']
