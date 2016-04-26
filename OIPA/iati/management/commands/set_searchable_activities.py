from django.core.management.base import BaseCommand
from iati.transaction.models import Transaction
from iati.models import Activity
from django.conf import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def update_searchable_activities(self):
        """
            Set all activities to searchable if the reporting org is in the settings.ROOT_ORGANISATIONS list
        """

        # set all non root activities as non searchable
        Activity.objects.exclude(reporting_organisations__ref__in=settings.ROOT_ORGANISATIONS).update(is_searchable=False)
        # loop through root activities and set children as searchable
        activities = Activity.objects.filter(reporting_organisations__ref__in=settings.ROOT_ORGANISATIONS)
        for activity in activities:
            activity.is_searchable = True
            activity.save()
            self.set_children_searchable(activity.iati_identifier)

    def set_children_searchable(self, iati_identifier):
        """
            sets all the children to searchable
            recursively calls itself but keeps a list of already set activities
        """

        provider_activity_transactions = Transaction.objects.filter(
            provider_organisation__provider_activity_id=iati_identifier)

        for transaction in provider_activity_transactions:
            activity = transaction.activity
            activity.is_searchable = True
            activity.save()
            self.set_children_searchable(activity.iati_identifier)
        return

    def handle(self, *args, **options):
        self.update_searchable_activities()



