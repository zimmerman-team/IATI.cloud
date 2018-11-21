from django.db import models
from django.db.models import Q


class OrganisationQuerySet(models.QuerySet):

    def get(self, *args, **kwargs):
        """
        Search in both 'id' and 'organisation_identifier' fields if querying
        by pk
        """
        if 'pk' in kwargs:
            pk = kwargs.get('pk')

            if pk:
                if isinstance(pk, self.model):
                    return pk

                try:
                    pk_int = int(pk)

                    return super(OrganisationQuerySet, self).get(
                        Q(pk=pk_int) | Q(organisation_identifier=pk_int))

                except ValueError:
                    return super(OrganisationQuerySet, self).get(
                        Q(organisation_identifier=pk)
                    )

        return super(OrganisationQuerySet, self).get(*args, **kwargs)

    # TODO: this makes counting a lot slower than it has to be for a lot of
    # queries
    def count(self):
        return super(OrganisationQuerySet, self).count()


class OrganisationManager(models.Manager):

    """Organisation manager """

    def get_queryset(self):
        return OrganisationQuerySet(self.model, using=self._db)
