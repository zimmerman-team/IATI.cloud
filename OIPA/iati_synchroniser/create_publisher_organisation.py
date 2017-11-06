from iati_codelists.models import Version, OrganisationType, Language
from iati_organisation.models import Organisation, OrganisationName, OrganisationReportingOrganisation, OrganisationNarrative


def create_publisher_organisation(publisher, publisher_iati_id, publisher_name, publisher_organization_type):
    version = Version.objects.get(code="2.02")

    try:
        org_type = OrganisationType.objects.get(code=publisher_organization_type)
    except OrganisationType.DoesNotExist:
        org_type = None

    org = Organisation(
        organisation_identifier=publisher_iati_id,
        normalized_organisation_identifier=publisher_iati_id,
        iati_standard_version=version,
        type=org_type,
        primary_name=publisher_name,
        published = True
    )
    org.save()

    org_name = OrganisationName(organisation=org)
    org_name.save()

    narrative = OrganisationNarrative(
        language=Language.objects.get(code='en'),
        content=publisher_name,
        related_object=org_name,
        organisation=org
    )
    narrative.save()

    org_reporter = OrganisationReportingOrganisation(
        organisation=org,
        org_type=org_type,
        reporting_org=org,
        reporting_org_identifier=publisher_iati_id,
        secondary_reporter=False
    )
    org_reporter.save()

    narrative = OrganisationNarrative(
        language=Language.objects.get(code='en'),
        content=publisher_name,
        related_object=org_reporter,
        organisation=org
    )
    narrative.save()

    publisher.organisation = org
    publisher.save()
    return publisher