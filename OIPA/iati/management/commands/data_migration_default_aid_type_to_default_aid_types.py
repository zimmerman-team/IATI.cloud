import sys
from django.core.management.base import BaseCommand

from iati.models import Activity, ActivityDefaultAidType


class Command(BaseCommand):
    """
    This process to migrations all default_aid_type related
    to the IATI V.2.02 or below to the default_aid_types for V.2.03.

    After this process, we can delete the field default_aid_type
    on the Activity.

    And change the relation name "default_aid_types" to "default_aid_type"
    on the ActivityDefaultAidType.

    This process to avoid is not consistence on the our system,
    so user is not confused because our system has
    two different default aid type for the same purpose.
    """

    def handle(self, *args, **options):
        # Check if activity has default_aid_type
        field_default_aid_type = Activity.__dict__.get('default_aid_type')
        if not field_default_aid_type:
            print(
                'Failed! The reason: '
                'default_aid_type in activity is not exists!'
            )

        # Check if activity has default_aid_types
        field_default_aid_type = Activity.__dict__.get('default_aid_types')
        if not field_default_aid_type:
            print(
                'Failed! The reason: '
                'default_aid_type in activity is not exists!'
            )

        # get all activity related to default_aid_type
        activities = Activity.objects.filter(default_aid_type__isnull=False)
        for activity in activities:
            print('Activity: {iati_identifier} in process'.format(
                iati_identifier=activity.iati_identifier
            ), end='\r')

            # Migration to ActivityDefaultAidType
            ActivityDefaultAidType.objects.get_or_create(
                activity=activity,
                aid_type_id=activity.default_aid_type_id
            )

            sys.stdout.write("\033[K")

        print("Successfully!")
