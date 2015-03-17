import datetime

# Django specific
from django.core.management.base import BaseCommand
from django.db import connection
from iati.models import Activity, Budget, Currency
import logging

logger = logging.getLogger(__name__)

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
            cur_act.total_budget_currency = self.get_budget_currency(cur_act);
            cur_act.save()

        return True

    def get_budget_currency(self, activity):

        try:
            current_currency = None
            for b in Budget.objects.filter(activity_id=activity.id):

                if not current_currency:
                    # first row
                    current_currency = b.currency_id
                elif current_currency == b.currency_id:
                    # currency matches previously found currency
                    continue
                else:
                    # multiple currencies detected, return None
                    return None

            if current_currency:
                return Currency.objects.get(code=current_currency)
            else:
                return None
        except Exception as e:
            logger.info("error in " + activity.id + ", def: get_budget_currency")
            if e.args:
                logger.info(e.args[0])
            if e.args.__len__() > 1:
                logger.info(e.args[1])
            if e.message:
                logger.info(e.message)
            return None



    def update_single_activity(self, id):

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT activity_id, sum(value) as total_value FROM iati_budget b WHERE activity_id ='" + id + "' GROUP BY activity_id")

            results = self.get_fields(cursor=cursor)
            for r in results:
                cur_act = Activity.objects.get(id=r['activity_id'])
                cur_act.total_budget = r['total_value']
                cur_act.total_budget_currency = self.get_budget_currency(cur_act)
                cur_act.save()
        except Exception as e:
            logger.info("error in " + id + ", def: update_single_activity")
            if e.args:
                logger.info(e.args[0])
            if e.args.__len__() > 1:
                logger.info(e.args[1])
            if e.message:
                logger.info(e.message)