# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from iati.models import Sector
from iati.models import Activity


class ProjectType(models.Model):
    sector = models.ForeignKey(Sector)
    activity = models.OneToOneField(Activity)

    def __unicode__(self,):
        return "%s - %s" % (self.activity.id, self.sector.code)
