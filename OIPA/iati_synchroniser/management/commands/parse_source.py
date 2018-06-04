from django.core.management.base import BaseCommand

from iati_synchroniser.models import Dataset


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('dataset_id', nargs=1, type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force parse the source (dont look at \
                 last-updated-datetimes)',
        )

    def handle(self, *args, **options):
        Dataset.objects.get(pk=options['dataset_id'][0]).process(
            force_reparse=options['force'])
