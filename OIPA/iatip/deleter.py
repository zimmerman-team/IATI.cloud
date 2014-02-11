__author__ = 'vincentvantwestende'

import iatip.models as models

class Deleter():

    def delete_by_source(self, xml_source_ref):
        activities = models.Activity.objects.filter(xml_source_ref=xml_source_ref)
        for activity in activities:
            self.remove_values_for_activity(activity)


    def return_first_exist(self, xpath_find):

        if not xpath_find:
             xpath_find = None
        else:
            try:
                xpath_find = unicode(xpath_find[0], errors='ignore')
            except:
                xpath_find = xpath_find[0]

            xpath_find = xpath_find.encode('utf-8')
        return xpath_find

    def remove_old_values_for_activity(self, elem):
        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
        activity_id = activity_id.replace(" ", "")
        cur_activity = models.Activity.objects.get(id=activity_id)
        self.remove_values_for_activity(cur_activity)

    def remove_values_for_activity(self, cur_activity):

        models.ActivityRecipientCountry.objects.filter(activity=cur_activity).delete()
        models.ActivitySector.objects.filter(activity=cur_activity).delete()
        models.ActivityWebsite.objects.filter(activity=cur_activity).delete()
        models.ActivityParticipatingOrganisation.objects.filter(activity=cur_activity).delete()
        models.ActivityPolicyMarker.objects.filter(activity=cur_activity).delete()
        models.ActivityRecipientRegion.objects.filter(activity=cur_activity).delete()
        models.RelatedActivity.objects.filter(current_activity=cur_activity).delete()
        models.OtherIdentifier.objects.filter(activity=cur_activity).delete()
        models.Title.objects.filter(activity=cur_activity).delete()
        models.Description.objects.filter(activity=cur_activity).delete()
        models.ContactInfo.objects.filter(activity=cur_activity).delete()
        models.Location.objects.filter(activity=cur_activity).delete()
        models.Transaction.objects.filter(activity=cur_activity).delete()
        models.Budget.objects.filter(activity=cur_activity).delete()
        models.PlannedDisbursement.objects.filter(activity=cur_activity).delete()
        models.Condition.objects.filter(activity=cur_activity).delete()
        models.Result.objects.filter(activity=cur_activity).delete()
        models.DocumentLink.objects.filter(activity=cur_activity).delete()
        cur_activity.delete()