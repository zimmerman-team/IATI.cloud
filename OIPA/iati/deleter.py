__author__ = 'vincentvantwestende'

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
        activity_id = self.return_first_exist(elem.xpath('iati-identifier/text()'))
        cur_activity = models.Activity.objects.get(iati_identifier=activity_id)
        self.remove_values_for_activity(cur_activity)

    def remove_old_values_for_activity_by_iati_id(self, iati_identifier):
        cur_activity = models.Activity.objects.get(iati_identifier=iati_identifier)
        self.remove_values_for_activity(cur_activity)

    def remove_old_values_for_activity_by_activity_id(self, activity_id):
        cur_activity = models.Activity.objects.get(id=activity_id)
        self.remove_values_for_activity(cur_activity)

    def remove_values_for_activity(self, cur_activity):

        try:
            models.ActivityParticipatingOrganisation.objects.filter(activity=cur_activity).delete()
            models.ActivityPolicyMarker.objects.filter(activity=cur_activity).delete()
            models.ActivitySector.objects.filter(activity=cur_activity).delete()
            models.ActivityRecipientCountry.objects.filter(activity=cur_activity).delete()

            models.CountryBudgetItem.objects.filter(activity=cur_activity).delete()
            models.ActivityRecipientRegion.objects.filter(activity=cur_activity).delete()
            models.OtherIdentifier.objects.filter(activity=cur_activity).delete()
            models.ActivityWebsite.objects.filter(activity=cur_activity).delete()

            models.ContactInfo.objects.filter(activity=cur_activity).delete()
            models.Transaction.objects.filter(activity=cur_activity).delete()
            models.PlannedDisbursement.objects.filter(activity=cur_activity).delete()
            models.DocumentLink.objects.filter(activity=cur_activity).delete()

            models.RelatedActivity.objects.filter(current_activity=cur_activity).delete()
            models.Title.objects.filter(activity=cur_activity).delete()
            models.Description.objects.filter(activity=cur_activity).delete()

            models.Location.objects.filter(activity=cur_activity).delete()
            models.Budget.objects.filter(activity=cur_activity).delete()
            models.Condition.objects.filter(activity=cur_activity).delete()

            models.ActivitySearchData.objects.filter(activity=cur_activity).delete()

            for r in models.Result.objects.filter(activity=cur_activity):
                for ri in models.ResultIndicator.objects.filter(result=r):
                    models.ResultIndicatorPeriod.objects.filter(result_indicator=ri).delete()
                    ri.delete()
                r.delete()

            for f in models.Ffs.objects.filter(activity=cur_activity):
                models.FfsForecast.objects.filter(ffs=f).delete()
                f.delete()

            for c in models.CrsAdd.objects.filter(activity=cur_activity):
                models.CrsAddLoanStatus.objects.filter(crs_add=c)
                models.CrsAddLoanTerms.objects.filter(crs_add=c)
                c.delete()

            cur_activity.delete()

        except Exception as e:
            exception_handler(e, cur_activity.id, "remove_values_for_activity")