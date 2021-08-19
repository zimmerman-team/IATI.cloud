from django.core.management.base import BaseCommand

from iati_synchroniser.dataset_syncer import DatasetSyncer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--iati_id', action='store', dest='iati_id')

    def handle(self, *args, **options):
        ds = DatasetSyncer()
        ds.synchronize_single_source_with_iati_api(options['iati_id'])
