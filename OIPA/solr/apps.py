from __future__ import unicode_literals

from django.apps import AppConfig


class SolrConfig(AppConfig):
    name = 'solr'
    verbose_name = 'SOLR'

    def ready(self):
        # pylint: disable=unused-variable
        import solr.signals  # NOQA: F401, W0612
