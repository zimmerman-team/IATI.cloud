from django.core.management.base import BaseCommand

from iati.activity_search_indexes import reindex_activity_by_source
from iati.models import Dataset


class Command(BaseCommand):

    def handle(self, *args, **options):
        for d in Dataset.objects.all():
            reindex_activity_by_source(d.id)
