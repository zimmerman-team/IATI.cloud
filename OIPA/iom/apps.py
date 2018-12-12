# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class IomConfig(AppConfig):
    name = 'iom'

    def ready(self):
        import iom.signals
