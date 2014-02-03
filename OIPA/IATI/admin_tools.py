from IATI.models import organisation
from IATI_synchroniser.models import Publisher

class AdminTools():

    def update_organisation_names(self):
        for o in organisation.objects.filter(name=None):
            try:
                organisation_code = o.code
                if Publisher.objects.exists(org_id=organisation_code):
                    publisher = Publisher.objects.get(org_id=organisation_code)
                    if o.abbreviation == None:
                        o.abbreviation = publisher.org_abbreviate
                    o.name = publisher.org_name
                    o.save()

            except Exception as e:
                print "error in update_organisation_names"
