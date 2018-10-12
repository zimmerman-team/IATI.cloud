from __future__ import unicode_literals

from django.apps import AppConfig


class IatiConfig(AppConfig):
    name = 'iati'
    verbose_name = 'IATI'

    def ready(self):
        import iati.transaction.signals  # NOQA: F401
