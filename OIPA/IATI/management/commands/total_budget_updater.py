import datetime

# Django specific
from django.core.management.base import BaseCommand
from django.db import connection
from iati.models import Activity, Budget


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    counter = 0

    def handle(self, *args, **options):
        parser = TotalBudgetUpdater()
        parser.updateTotal()


class TotalBudgetUpdater():

    def get_fields(self, cursor):
        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
        return results

    def update(self):

        cursor = connection.cursor()
        cursor.execute('SELECT activity_id, sum(value) as total_value FROM IATI_budget b GROUP BY activity_id')

        results = self.get_fields(cursor=cursor)
        for r in results:
            cur_act = Activity.objects.get(id=r['activity_id'])
            cur_act.total_budget = r['total_value']
            cur_act.save()

        return True


    def update_single_activity(self, id):

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT activity_id, sum(value) as total_value FROM IATI_budget b WHERE activity_id ='" + id + "' GROUP BY activity_id")

            results = self.get_fields(cursor=cursor)
            for r in results:
                cur_act = Activity.objects.get(id=r['activity_id'])
                cur_act.total_budget = r['total_value']
                cur_act.save()
        except Exception as e:
            print e.message