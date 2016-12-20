
from iati.factory.iati_factory import *
from iati.transaction.factories import *

def _create_test_narrative(activity, related_object, content):
    NarrativeFactory.create(activity=activity, related_object=related_object, content=content)

def _create_test_transaction(
    activity,
    transaction_type,
    value):

    TransactionFactory.create(
        activity=second_activity,
        value=25000,
        transaction_type=first_transaction.transaction_type)

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
    other_identifier1="other_idenifier1",
    other_identifier2="other_idenifier2",
    document_link1="document_link_title1",
    document_link2="document_link_title2",
    transaction_description1_1="transaction_description1_1",
    transaction_description1_2="transaction_description1_2",
    transaction_description2_1="transaction_description2_1",
    transaction_description2_2="transaction_description2_2",
    transaction_provider_org1_1="transaction_provider_org1_1",
    transaction_provider_org1_2="transaction_provider_org1_2",
    transaction_provider_org2_1="transaction_provider_org2_1",
    transaction_provider_org2_2="transaction_provider_org2_2",
    transaction_receiver_org1_1="transaction_receiver_org1_1",
    transaction_receiver_org1_2="transaction_receiver_org1_2",
    transaction_receiver_org2_1="transaction_receiver_org2_1",
    transaction_receiver_org2_2="transaction_receiver_org2_2",
    location_name1_1="location_name1_1",
    location_name1_2="location_name1_2",
    location_description1_1="location_description1_1",
    location_description1_2="location_description1_2",
    location_activity_description1_1="location_activity_description1_1",
    location_activity_description1_2="location_activity_description1_2",
        ):
    """
    For testing narratives (hence search)
    """

    activity = ActivityFactory.create(
        id=iati_identifier,
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
    )

    _create_test_narrative(activity, sector, sector1)
    _create_test_narrative(activity, sector, sector2)

    document_link = DocumentLinkFactory.create(
        activity=activity,
    )

    document_link_category = DocumentLinkCategoryFactory.create(
        document_link=document_link,
    )
    document_link_language = DocumentLinkLanguageFactory.create(
        document_link=document_link,
    )

    _create_test_narrative(activity, document_link.documentlinktitle, document_link1)
    _create_test_narrative(activity, document_link.documentlinktitle, document_link2)

    other_identifier = OtherIdentifierFactory.create(
        activity=activity,
        )
    _create_test_narrative(activity, other_identifier, other_identifier1)
    _create_test_narrative(activity, other_identifier, other_identifier2)

    transaction1 = TransactionFactory.create(activity=activity)
    transaction_description1 = TransactionDescriptionFactory.create(transaction=transaction1)
    provider_org1 = TransactionProviderFactory.create(transaction=transaction1, provider_activity=activity) 
    receiver_org1 = TransactionReceiverFactory.create(transaction=transaction1, receiver_activity=activity) 
    transaction_recipient_country1 = TransactionRecipientCountryFactory.create(transaction=transaction1) 
    transaction_recipient_region1 = TransactionRecipientRegionFactory.create(transaction=transaction1) 
    transaction_sector1 = TransactionSectorFactory.create(transaction=transaction1) 

    _create_test_narrative(activity, transaction_description1, transaction_description1_1)
    _create_test_narrative(activity, transaction_description1, transaction_description1_2)
    _create_test_narrative(activity, provider_org1, transaction_provider_org1_1)
    _create_test_narrative(activity, provider_org1, transaction_provider_org1_2)
    _create_test_narrative(activity, receiver_org1, transaction_receiver_org1_1)
    _create_test_narrative(activity, receiver_org1, transaction_receiver_org1_2)

    # transaction2 = TransactionFactory.create(activity=activity)

#     location1 = LocationFactory.create(activity=activity)
#     location_name1 = LocationNameFactory.create(location=location1)
#     location_description1 = LocationDescriptionFactory.create(location=location1)
#     location_activity_description1 = LocationActivityDescriptionFactory.create(location=location1)

#     _create_test_narrative(activity, location_name1, transaction_name1_1)
#     _create_test_narrative(activity, location_name1, transaction_name1_2)
#     _create_test_narrative(activity, location_description1, transaction_description1_1)
#     _create_test_narrative(activity, location_description1, transaction_description1_2)
#     _create_test_narrative(activity, location_activity_description1, transaction_activity_description1_1)
#     _create_test_narrative(activity, location_activity_description1, transaction_activity_description1_2)


    return activity


