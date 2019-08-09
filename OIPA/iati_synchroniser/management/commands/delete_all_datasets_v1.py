from django.core.management.base import BaseCommand

from iati_synchroniser.models import Dataset


class Command(BaseCommand):
    """
    This command to delete all dataset with version below then 2.01
    """

    def handle(self, *args, **options):
        Dataset.objects.exclude(
            iati_version__in=['2.01', '2.02', '2.03']
        ).delete()

        print('Done!')
