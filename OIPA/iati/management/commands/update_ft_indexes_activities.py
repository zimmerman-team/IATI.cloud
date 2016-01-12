
from django.core.management.base import BaseCommand
from django.conf import settings

from iati.models import Activity
from iati.activity_search_indexes import reindex_all_activities, reindex_activity, reindex_activity_by_source

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    """
        Reindex full text search values for all activities
    """

    def add_arguments(self, parser):
        parser.add_argument('--activity',
            action='store',
            dest='activity',
            default=None,
            help='Reindex only this activity')

        parser.add_argument('--source',
            action='store',
            dest='source',
            default=None,
            help='Reindex only activities with this xml_source_ref')


    def handle(self, *args, **options):
        if options['activity']:
            activity = Activity.objects.get(iati_identifier=options['activity'])
            reindex_activity(activity)
        elif options['source']:
            reindex_activity_by_source(options['source'])
        else:
            reindex_all_activities()



