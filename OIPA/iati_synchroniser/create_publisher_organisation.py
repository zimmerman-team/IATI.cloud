from iati_codelists.models import Version, OrganisationType, Language
from iati_organisation.models import Organisation
from iati_organisation.models import OrganisationName
from iati_organisation.models import OrganisationReportingOrganisation
from iati_organisation.models import OrganisationNarrative


def create_publisher_organisation(publisher, publisher_organization_type):
    version = Version.objects.get(code="2.02")
    language = Language.objects.get(code='en')
    
    try:
        org_type = OrganisationType.objects.get(code=publisher_organization_type)
    except OrganisationType.DoesNotExist:
        org_type = None

    org = Organisation.objects.create(
        organisation_identifier=publisher.publisher_iati_id,
        normalized_organisation_identifier=publisher.publisher_iati_id,
        iati_standard_version=version,
        type=org_type,
        primary_name=publisher.display_name,
        published = True
    )

    org_name = OrganisationName.objects.create(organisation=org)

    OrganisationNarrative.objects.create(
        language=language,
        content=publisher.display_name,
        related_object=org_name,
        organisation=org
    )

    org_reporter = OrganisationReportingOrganisation.objects.create(
        organisation=org,
        org_type=org_type,
        reporting_org=org,
        reporting_org_identifier=publisher.publisher_iati_id,
        secondary_reporter=False
    )

    OrganisationNarrative.objects.create(
        language=language,
        content=publisher.display_name,
        related_object=org_reporter,
        organisation=org
    )

    publisher.organisation = org
    publisher.save()
    return publisher
