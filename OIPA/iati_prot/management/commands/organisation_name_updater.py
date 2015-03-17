from django.core.management.base import BaseCommand
from iati.models import Organisation
from iati_synchroniser.models import Publisher

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    counter = 0

    def handle(self, *args, **options):
        updater = OrganisationNameUpdater()
        updater.update()


class OrganisationNameUpdater():

    def update(self):
        for o in Organisation.objects.filter(name=None):
            try:
                organisation_code = o.code
                if Publisher.objects.exists(org_id=organisation_code):
                    current_publisher = Publisher.objects.get(org_id=organisation_code)
                    if o.abbreviation == None:
                        o.abbreviation = current_publisher.org_abbreviate
                    o.name = current_publisher.org_name
                    o.save()

            except Exception as e:
                print "error in update_organisation_names"

        return True