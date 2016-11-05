from django.core.management.base import BaseCommand
from iati_synchroniser.dataset_syncer import DatasetSyncer

class Command(BaseCommand):

    def handle(self, *args, **options):

        ds = DatasetSyncer()
        ds.synchronize_with_iati_api()

