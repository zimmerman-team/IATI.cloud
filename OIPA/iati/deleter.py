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
        print 'in deleter '+iati_identifier
        cur_activity = models.Activity.objects.get(iati_identifier=iati_identifier)
        self.remove_values_for_activity(cur_activity)

    def remove_old_values_for_activity_by_activity_id(self, activity_id):
        cur_activity = models.Activity.objects.get(id=activity_id)
        self.remove_values_for_activity(cur_activity)



    def remove_values_for_activity(self, cur_activity):

        try:
            models.Narrative.objects.filter(iati_identifier=cur_activity.iati_identifier).delete()
            models.Title.objects.filter(activity=cur_activity).delete()

            models.ActivityParticipatingOrganisation.objects.filter(activity=cur_activity).delete()
            models.ActivityPolicyMarker.objects.filter(activity=cur_activity).delete()
            models.ActivitySector.objects.filter(activity=cur_activity).delete()
            models.ActivityRecipientCountry.objects.filter(activity=cur_activity).delete()

            models.CountryBudgetItem.objects.filter(activity=cur_activity).delete()
            models.ActivityRecipientRegion.objects.filter(activity=cur_activity).delete()
            models.OtherIdentifier.objects.filter(activity=cur_activity).delete()
            models.ActivityWebsite.objects.filter(activity=cur_activity).delete()

            for contact_info in models.ContactInfo.objects.filter(activity=cur_activity):
                models.ContactInfoPersonName.objects.filter(contact_info=contact_info).delete()
                models.ContactInfoOrganisation.objects.filter(contact_info=contact_info).delete()
                models.ContactInfoMailingAddress.objects.filter(contact_info=contact_info).delete()
                models.ContactInfoJobTitle.objects.filter(contact_info=contact_info).delete()
               
                contact_info.delete()


            for trans in models.Transaction.objects.filter(activity=cur_activity):
                models.TransactionDescription.objects.filter(Transaction=trans).delete()
                models.TransactionProvider.objects.filter(Transaction=trans).delete()
                models.TransactionSector.objects.filter(Transaction=trans).delete()
                models.TransactionReciever.objects.filter(Transaction=trans).delete()

            models.Transaction.objects.filter(activity=cur_activity).delete()
            models.PlannedDisbursement.objects.filter(activity=cur_activity).delete()
            for doc_link in models.DocumentLink.objects.filter(activity=cur_activity):
                models.DocumentLinkTitle.objects.filter(document_link=doc_link).delete()

                doc_link.delete()

            models.RelatedActivity.objects.filter(current_activity=cur_activity).delete()
            models.Title.objects.filter(activity=cur_activity).delete()
            models.Description.objects.filter(activity=cur_activity).delete()

            for loc in models.Location.objects.filter(activity=cur_activity):
                models.LocationName.objects.filter(location=loc).delete()
                models.LocationDescription.objects.filter(location=loc).delete()
                models.LocationActivityDescription.objects.filter(location=loc).delete()
                loc.delete()

            for budget_item in models.Budget.objects.filter(activity=cur_activity):
                models.BudgetItemDescription.objects.filter(budget_item=budget_item).delete()
                budget_item.delete()

            models.Condition.objects.filter(activity=cur_activity).delete()

            models.ActivitySearchData.objects.filter(activity=cur_activity).delete()


            for r in models.Result.objects.filter(activity=cur_activity):
                models.ResultTitle.objects.filter(result=r).delete()
                for ri in models.ResultIndicator.objects.filter(result=r):

                    models.ResultIndicatorPeriod.objects.filter(result_indicator=ri).delete()
                    models.ResultIndicatorTitle.objects.filter(result_indicator=ri).delete()
                    models.ResultIndicatorDescription.objects.filter(result_indicator=ri).delete()
                    models.ResultIndicatorBaseLineComment.objects.filter(result_indicator=ri).delete()
                    for rip in models.ResultIndicatorPeriod.objects.filter(result_indicator=ri):
                        models.ResultIndicatorPeriodTargetComment.objects.filter(result_indicator_period=rip).delete()
                        models.ResultIndicatorPeriodActualComment.objects.filter(result_indicator_period=rip).delete()
                        rip.delete()
                    
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