__author__ = 'vincentvantwestende'

import IATI.models as models

class Deleter():

    def delete_by_source(self, xml_source_ref):
        print ""

        activities = models.activity.objects.filter(xml_source_ref=xml_source_ref)
        for activity in activities:
            self.remove_values_for_activity(activity)


    def return_first_exist(xpath_find):

        if not xpath_find:
             xpath_find = None
        else:
            # xpath_find = xpath_find[0].encode('utf-8')
            try:
                xpath_find = unicode(xpath_find[0], errors='ignore')
            except:
                xpath_find = xpath_find[0]

            xpath_find = xpath_find.encode('utf-8')
        return xpath_find


    def remove_old_values_for_activity(self, elem):

        activity_id = self.return_first_exist(elem.xpath( 'iati-identifier/text()' ))
        activity_id = activity_id.replace(" ", "")
        cur_activity = models.activity.objects.get(id=activity_id)
        self.remove_values_for_activity(cur_activity)


    def remove_values_for_activity(self, cur_activity):
        models.activity_recipient_country.objects.filter(activity=cur_activity).delete()
        models.activity_sector.objects.filter(activity=cur_activity).delete()
        models.activity_date.objects.filter(activity=cur_activity).delete()
        models.activity_website.objects.filter(activity=cur_activity).delete()
        models.activity_participating_organisation.objects.filter(activity=cur_activity).delete()
        models.activity_policy_marker.objects.filter(activity=cur_activity).delete()
        models.activity_recipient_region.objects.filter(activity=cur_activity).delete()
        models.related_activity.objects.filter(current_activity=cur_activity).delete()
        models.other_identifier.objects.filter(activity=cur_activity).delete()
        models.title.objects.filter(activity=cur_activity).delete()
        models.description.objects.filter(activity=cur_activity).delete()
        models.contact_info.objects.filter(activity=cur_activity).delete()
        models.location.objects.filter(activity=cur_activity).delete()
        models.transaction.objects.filter(activity=cur_activity).delete()
        models.budget.objects.filter(activity=cur_activity).delete()
        models.planned_disbursement.objects.filter(activity=cur_activity).delete()
        models.condition.objects.filter(activity=cur_activity).delete()
        models.result.objects.filter(activity=cur_activity).delete()
        models.document_link.objects.filter(activity=cur_activity).delete()
        cur_activity.delete()