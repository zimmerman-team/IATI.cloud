"""
Methods triggered after activity has been parsed
"""
from iati.models import ActivityReportingOrganisation

def set_activity_reporting_organisation(organisation):
    """ update ActivityParticipatingOrganisation.organisation references to this organisation """
    ActivityReportingOrganisation.objects.filter(
        organisation=None, 
        ref=organisation.organisation_identifier
    ).update(organisation=organisation)
