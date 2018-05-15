from django.db import models
from django.db.models import Prefetch
from iati.djorm_pgfulltext.models import SearchManagerMixIn, SearchQuerySet


class DocumentQuerySet(SearchQuerySet):

    # TODO: this makes counting a lot slower than it has to be for a lot of queries
    def count(self):
        self = self.order_by().only('id')
        return super(DocumentQuerySet, self).count()

    # TODO: fix import conflicts - 2016-01-18
    def prefetch_all(self):

        return self.prefetch_content()

    def prefetch_content(self):
        from iati.models import DocumentLink

        return self.prefetch_related(
            Prefetch(
                'documentlink_set',
                queryset=DocumentLink.objects.all()
                .select_related('activity')))


class DocumentManager(SearchManagerMixIn, models.Manager):

    """Document manager with search capabilities"""

    def get_queryset(self):
        return DocumentQuerySet(self.model, using=self._db)
