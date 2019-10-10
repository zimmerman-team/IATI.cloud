from __future__ import unicode_literals

from django.apps import AppConfig


class SolrConfig(AppConfig):
    name = 'solr'
    verbose_name = 'SOLR'

    """
    # pylint: disable=no-self-use
    def ready(self):  # NOQA: R0201
        # pylint: disable=unused-variable
        import solr.signals  # NOQA: F401, W0612
    """
