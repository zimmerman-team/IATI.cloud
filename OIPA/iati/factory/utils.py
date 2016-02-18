
from iati.factory.iati_factory import *

def _create_test_narrative(activity, related_object, content):
    NarrativeFactory.create(activity=activity, related_object=related_object, content=content)

def _create_test_activity(
    id="IATI-search1",
    iati_identifier="IATI-search1",
    title1="title1",
    title2="title2",
    description1_1="description1_1",
    description1_2="description1_2",
    description2_1="description2_1",
    description2_2="description2_2",
    reporting_organisation1="reporting_organisation1",
    reporting_organisation2="reporting_organisation2",
    participating_organisation1="participating_organisation1",
    participating_organisation2="participating_organisation2",
    recipient_country1="recipient_country1",
    recipient_country2="recipient_country2",
    recipient_region1="recipient_region1",
    recipient_region2="recipient_region2",
    sector1="sector1",
    sector2="sector2",
    document_link_title1="document_link_title1",
    document_link_title2="document_link_title2",
        ):
    """
    For testing narratives (hence search)
    """

    activity = ActivityFactory.create(
        id=id,
        iati_identifier=iati_identifier
    )

    title = TitleFactory.create(
        activity=activity,
        )

    _create_test_narrative(activity, title, title1)
    _create_test_narrative(activity, title, title2)

    description1 = DescriptionFactory.create(
        activity=activity,
        )

    _create_test_narrative(activity, description1, description1_1)
    _create_test_narrative(activity, description1, description1_2)

    description2 = DescriptionFactory.create(
        activity=activity,
        )

    _create_test_narrative(activity, description2, description2_1)
    _create_test_narrative(activity, description2, description2_2)

    reporting_organisation = ReportingOrganisationFactory.create(
        activity=activity,
    )

    _create_test_narrative(activity, reporting_organisation, reporting_organisation1)
    _create_test_narrative(activity, reporting_organisation, reporting_organisation2)

    participating_organisation = ParticipatingOrganisationFactory.create(
        activity=activity,
    )

    _create_test_narrative(activity, participating_organisation, participating_organisation1)
    _create_test_narrative(activity, participating_organisation, participating_organisation2)

    recipient_country = ActivityRecipientCountryFactory.create(
        activity=activity,
    )

    _create_test_narrative(activity, recipient_country, recipient_country1)
    _create_test_narrative(activity, recipient_country, recipient_country2)

    recipient_region = ActivityRecipientRegionFactory.create(
        activity=activity,
    )

    _create_test_narrative(activity, recipient_region, recipient_region1)
    _create_test_narrative(activity, recipient_region, recipient_region2)

    sector = ActivitySectorFactory.create(
        activity=activity,
        narrative1=_create_test_narrative(sector1),
        narrative2=_create_test_narrative(sector2),
    )

    _create_test_narrative(activity, sector, sector1)
    _create_test_narrative(activity, sector, sector2)

    document_link = DocumentLinkFactory.create(
        activity=activity,
    )

    document_link_title = DocumentLinkTitleFactory.create(
        document_link=document_link,
    )

    _create_test_narrative(activity, document_link_title, sector1)
    _create_test_narrative(activity, document_link_title, sector2)

    return activity


