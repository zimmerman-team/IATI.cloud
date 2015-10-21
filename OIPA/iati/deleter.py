import iati.models as models
from iati_synchroniser.exception_handler import exception_handler


class Deleter():

    def delete_by_source(self, xml_source_ref):
        try:
            activities = models.Activity.objects.filter(xml_source_ref=xml_source_ref)
            for activity in activities:
                self.remove_values_for_activity(activity)

        except Exception as e:
            exception_handler(e, xml_source_ref, "delete_by_source")

    def remove_old_values_for_activity_by_activity_id(self, activity_id):
        cur_activity = models.Activity.objects.get(id=activity_id)
        self.remove_values_for_activity(cur_activity)

    def delete_all_activities(self):
        # hard delete all activities
        for activity in models.Activity.objects.all():
            self.remove_values_for_activity(activity)

    def remove_values_for_activity(self, activity):
        activity.delete()
        # TO DO : delete 
        # iati_transactionreceiver
        # iati_transactionprovider
        # iati_title
