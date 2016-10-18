from django.db import models
from django.contrib.auth.models import Group, User

from iati_synchroniser.models import Publisher

class AdminGroup(Group):
    # every group is associated with exactly one publisher
    publisher = models.ForeignKey(Publisher, unique=True)
    owner = models.ForeignKey(User)

    class Meta:
        verbose_name_plural = "AdminGroups"
        ordering = ['name']

