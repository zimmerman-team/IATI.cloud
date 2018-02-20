from django.core.management.base import BaseCommand
from iati_synchroniser.create_publisher_organisation import create_publisher_organisation
from iati_synchroniser.models import Publisher


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('identifier', nargs=1, help='organisation identifier')
        parser.add_argument('name', nargs=1, help='organisation name')
        parser.add_argument('organisation_type', nargs=1, help='organisation type')

    def handle(self, *args, **options):
        publisher, created = Publisher.objects.update_or_create(
            iati_id=options['identifier'][0],
            defaults={
                'publisher_iati_id': options['identifier'][0],
                'name': options['name'][0],
                'display_name': options['name'][0]
            }
        )

        publisher.save()
        create_publisher_organisation(
            publisher,
            options['identifier'][0],
            options['name'][0],
            options['organisation_type'][0]
        )
