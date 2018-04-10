from django.db import models
from django.db.models import Prefetch


class LocationQuerySet(models.QuerySet):

    def count(self):
        self = self.order_by().only('id')
        return super(LocationQuerySet, self).count()

    # def prefetch_location_reach(self):
    #     return self.select_related('location_reach')

    # def prefetch_exactness(self):
    #     return self.select_related('exactness')

    # def prefetch_location_class(self):
    #     return self.select_related('location_class')

    def prefetch_feature_designation(self):
        return self.select_related('feature_designation__category')

    def prefetch_location_id(self):
        return self.select_related('location_id_vocabulary')

    def prefetch_administrative(self):
        from iati.models import LocationAdministrative

        return self.prefetch_related(
            Prefetch(
                'locationadministrative_set',
                queryset=LocationAdministrative.objects
                .select_related('vocabulary')),)

    def prefetch_name(self):
        from iati.models import LocationName, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))
        return self.prefetch_related(
            Prefetch(
                'name',
                queryset=LocationName.objects
                .prefetch_related(narrative_prefetch)),)

    def prefetch_description(self):
        from iati.models import LocationDescription, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'description',
                queryset=LocationDescription.objects
                .prefetch_related(narrative_prefetch)),)

    def prefetch_activity_description(self):
        from iati.models import LocationActivityDescription, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'activity_description',
                queryset=LocationActivityDescription.objects.all()
                .prefetch_related(narrative_prefetch)),)

    def prefetch_activity(self):
        from iati.models import Activity, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'activity__title__narratives',
                queryset=Narrative.objects
                .select_related('language'))
        )


class LocationManager(models.Manager):

    def get_queryset(self):
        return LocationQuerySet(self.model, using=self._db)
