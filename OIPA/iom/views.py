# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from iom import serializers as activity_serializers
from api.activity.views import ActivityList as ParentActivityList


class ActivityList(ParentActivityList):
    serializer_class = activity_serializers.ActivitySerializer
