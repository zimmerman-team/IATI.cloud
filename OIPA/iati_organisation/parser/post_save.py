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

    try:
        publisher = Publisher.objects.get(publisher_iati_id=organisation.organisation_identifier)
        publisher.organisation = organisation
        publisher.save()
    except Publisher.DoesNotExist:
        return
    except Publisher.MultipleObjectsReturned:
        return

