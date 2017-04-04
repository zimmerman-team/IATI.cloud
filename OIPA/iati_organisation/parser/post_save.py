"""
Methods triggered after activity has been parsed
"""
from iati.models import ActivityReportingOrganisation
from iati_synchroniser.models import Publisher

def set_activity_reporting_organisation(organisation):
    """ update ActivityParticipatingOrganisation.organisation references to this organisation """
    ActivityReportingOrganisation.objects.filter(
        organisation=None, 
        ref=organisation.organisation_identifier
    ).update(organisation=organisation)

def set_publisher_fk(organisation):
    if not organisation:
        return
    print organisation
    print(organisation.id)
    try:
        publisher = Publisher.objects.get(pk=organisation.id)
        publisher.organisation = organisation
        publisher.save()

    except Publisher.DoesNotExist:
        return

