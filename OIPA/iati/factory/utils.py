from iati.factory.iati_factory import (
    ActivityDateFactory, ActivityFactory, ActivityPolicyMarkerFactory,
    ActivityRecipientCountryFactory, ActivityRecipientRegionFactory,
    ActivitySectorFactory, BudgetFactory, BudgetItemFactory, ConditionFactory,
    ConditionsFactory, ContactInfoDepartmentFactory, ContactInfoFactory,
    ContactInfoJobTitleFactory, ContactInfoMailingAddressFactory,
    ContactInfoOrganisationFactory, ContactInfoPersonNameFactory,
    CountryBudgetItemFactory, CrsAddFactory, CrsAddOtherFlagsFactory,
    DescriptionFactory, DocumentLinkCategoryFactory, DocumentLinkFactory,
    DocumentLinkLanguageFactory, FssFactory, FssForecastFactory,
    HumanitarianScopeFactory, LegacyDataFactory, LocationAdministrativeFactory,
    LocationFactory, NarrativeFactory, OrganisationFactory,
    OrganisationNarrativeFactory, OtherIdentifierFactory,
    ParticipatingOrganisationFactory, PlannedDisbursementFactory,
    PlannedDisbursementProviderFactory, PlannedDisbursementReceiverFactory,
    RelatedActivityFactory, ResultFactory, ResultIndicatorFactory,
    ResultIndicatorPeriodActualDimensionFactory,
    ResultIndicatorPeriodActualLocationFactory, ResultIndicatorPeriodFactory,
    ResultIndicatorPeriodTargetDimensionFactory,
    ResultIndicatorPeriodTargetFactory,
    ResultIndicatorPeriodTargetLocationFactory,
    ResultIndicatorReferenceFactory, TitleFactory, ResultIndicatorPeriodTargetCommentFactory
)
from iati.transaction.factories import (
    TransactionDescriptionFactory, TransactionFactory,
    TransactionProviderFactory, TransactionReceiverFactory,
    TransactionRecipientCountryFactory, TransactionRecipientRegionFactory,
    TransactionSectorFactory
)


def _create_test_narrative(activity, related_object, content,
                           is_organisation_narrative=False):
    if not is_organisation_narrative:
        NarrativeFactory.create(
            activity=activity, related_object=related_object, content=content)
    else:
        OrganisationNarrativeFactory.create(
            organisation=activity,
            related_object=related_object,
            content=content)


def _create_test_activity(
    id="IATI-search1",
    iati_identifier="IATI-search1",
    title1="title1",
    title2="title2",
    capital_spend="88.80",
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
    condition1_narrative_1="Conditions text",
    condition1_narrative_2="Conditions texte",
    condition2_narrative_1="Conditions text2",
    condition2_narrative_2="Conditions texte2",
    organisation_narrative_1="Agency A",
    department_narrative_1="Department B",
    person_name_narrative_1="A. Example",
    job_title_narrative_1="Transparency Lead",
    mailing_address_narrative_1="Transparency House, The Street, Town, City, Postcode",  # NOQA: E501
    budget_item_description_narrative_1="Description text",
    planned_disbursement_provider_narrative_1="Agency B",
    planned_disbursement_receiver_narrative_1="Agency A",
    resulttitle_narrative_1="Result title",
    resultdescription_narrative_1="Result description text",
    resultindicatortitle_narrative_1="Indicator title",
    resultindicatordescription_narrative_1="Indicator description text",
    resultindicatorbaselinecomment_narrative_1="Baseline comment text",
    resultindicatorperiodtargetcomment_narrative_1="Target comment text",
    resultindicatorperiodactualcomment_narrative_1="Actual comment text",
):
    """
    For testing narratives (hence search)
    """

    activity = ActivityFactory.create(
        iati_identifier=iati_identifier,
        capital_spend=capital_spend
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

    organisation = OrganisationFactory.create()

    _create_test_narrative(organisation, organisation.name,
                           reporting_organisation1, True)
    _create_test_narrative(organisation, organisation.name,
                           reporting_organisation2, True)

    participating_organisation = ParticipatingOrganisationFactory.create(
        activity=activity,
    )

    _create_test_narrative(
        activity, participating_organisation, participating_organisation1)
    _create_test_narrative(
        activity, participating_organisation, participating_organisation2)

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

    DocumentLinkCategoryFactory.create(
        document_link=document_link,
    )
    DocumentLinkLanguageFactory.create(
        document_link=document_link,
    )

    _create_test_narrative(
        activity, document_link.documentlinktitle, document_link1)
    _create_test_narrative(
        activity, document_link.documentlinktitle, document_link2)

    other_identifier = OtherIdentifierFactory.create(
        activity=activity,
    )
    _create_test_narrative(activity, other_identifier, other_identifier1)
    _create_test_narrative(activity, other_identifier, other_identifier2)

    transaction1 = TransactionFactory.create(activity=activity)
    transaction_description1 = TransactionDescriptionFactory.create(
        transaction=transaction1)
    provider_org1 = TransactionProviderFactory.create(
        transaction=transaction1, provider_activity=activity)
    receiver_org1 = TransactionReceiverFactory.create(
        transaction=transaction1, receiver_activity=activity)
    TransactionRecipientCountryFactory.create(
        transaction=transaction1)
    TransactionRecipientRegionFactory.create(
        transaction=transaction1)
    TransactionSectorFactory.create(
        transaction=transaction1)

    _create_test_narrative(
        activity, transaction_description1, transaction_description1_1)
    _create_test_narrative(
        activity, transaction_description1, transaction_description1_2)
    _create_test_narrative(activity, provider_org1,
                           transaction_provider_org1_1)
    _create_test_narrative(activity, provider_org1,
                           transaction_provider_org1_2)
    _create_test_narrative(activity, receiver_org1,
                           transaction_receiver_org1_1)
    _create_test_narrative(activity, receiver_org1,
                           transaction_receiver_org1_2)

    location = LocationFactory.create(activity=activity)
    _create_test_narrative(activity, location.name, location_name1_1)
    _create_test_narrative(activity, location.description,
                           location_description1_1)
    _create_test_narrative(
        activity,
        location.activity_description,
        location_activity_description1_1)
    LocationAdministrativeFactory.create(
        location=location)

    BudgetFactory.create(activity=activity)

    conditions1 = ConditionsFactory.create(activity=activity)
    condition1 = ConditionFactory.create(conditions=conditions1)
    _create_test_narrative(activity, condition1, condition1_narrative_1)
    _create_test_narrative(activity, condition1, condition1_narrative_2)
    condition2 = ConditionFactory.create(conditions=conditions1)
    _create_test_narrative(activity, condition2, condition2_narrative_1)
    _create_test_narrative(activity, condition2, condition2_narrative_2)

    contact_info1 = ContactInfoFactory.create(activity=activity)
    contactinfoorganisation1 = ContactInfoOrganisationFactory.create(
        contact_info=contact_info1)
    _create_test_narrative(
        activity, contactinfoorganisation1, organisation_narrative_1)
    ContactInfoDepartmentFactory.create(
        contact_info=contact_info1)
    _create_test_narrative(
        activity, contact_info1.department, department_narrative_1)
    contactinfopersonname1 = ContactInfoPersonNameFactory.create(
        contact_info=contact_info1)
    _create_test_narrative(
        activity, contactinfopersonname1, person_name_narrative_1)
    contactinfojobtitle1 = ContactInfoJobTitleFactory.create(
        contact_info=contact_info1)
    _create_test_narrative(
        activity, contactinfojobtitle1, job_title_narrative_1)
    contactinfomailingaddress1 = ContactInfoMailingAddressFactory.create(
        contact_info=contact_info1)
    _create_test_narrative(
        activity, contactinfomailingaddress1, mailing_address_narrative_1)

    country_budget_item = CountryBudgetItemFactory.create(activity=activity)
    budget_item = BudgetItemFactory.create(
        country_budget_item=country_budget_item)
    _create_test_narrative(activity, budget_item.description,
                           budget_item_description_narrative_1)

    HumanitarianScopeFactory(activity=activity)

    LegacyDataFactory.create(activity=activity)
    LegacyDataFactory.create(activity=activity)

    crs_add = CrsAddFactory.create(activity=activity)
    CrsAddOtherFlagsFactory.create(crs_add=crs_add)

    RelatedActivityFactory.create(current_activity=activity)

    ActivityPolicyMarkerFactory.create(
        activity=activity,
    )

    ActivityDateFactory.create(activity=activity)

    planned_disbursement = PlannedDisbursementFactory.create(activity=activity)
    planned_disbursement_provider = PlannedDisbursementProviderFactory.create(
        planned_disbursement=planned_disbursement)
    _create_test_narrative(activity, planned_disbursement_provider,
                           planned_disbursement_provider_narrative_1)
    planned_disbursement_receiver = PlannedDisbursementReceiverFactory.create(
        planned_disbursement=planned_disbursement)
    _create_test_narrative(activity, planned_disbursement_receiver,
                           planned_disbursement_receiver_narrative_1)

    result = ResultFactory(activity=activity)
    _create_test_narrative(activity, result.resulttitle,
                           resulttitle_narrative_1)
    _create_test_narrative(
        activity, result.resultdescription, resultdescription_narrative_1)
    result_indicator = ResultIndicatorFactory.create(result=result)
    _create_test_narrative(
        activity,
        result_indicator.resultindicatortitle,
        resultindicatortitle_narrative_1)
    _create_test_narrative(
        activity,
        result_indicator.resultindicatordescription,
        resultindicatordescription_narrative_1)
    ResultIndicatorReferenceFactory.create(
        result_indicator=result_indicator)
    _create_test_narrative(
        activity,
        result_indicator.resultindicatorbaselinecomment,
        resultindicatorbaselinecomment_narrative_1)
    result_indicator_period = ResultIndicatorPeriodFactory.create(
        result_indicator=result_indicator)

    result_indicator_period_target = ResultIndicatorPeriodTargetFactory(
        result_indicator_period=result_indicator_period
    )
    ResultIndicatorPeriodTargetCommentFactory(
        result_indicator_period_target=result_indicator_period_target
    )
    # NEW^
    ResultIndicatorPeriodTargetLocationFactory.create(
        result_indicator_period_target=result_indicator_period_target)
    ResultIndicatorPeriodTargetDimensionFactory.create(
        result_indicator_period_target=result_indicator_period_target)
    _create_test_narrative(
        activity,
        result_indicator_period_target.resultindicatorperiodtargetcomment_set.first(),
        resultindicatorperiodtargetcomment_narrative_1)
    ResultIndicatorPeriodActualLocationFactory.create(
        result_indicator_period=result_indicator_period)
    ResultIndicatorPeriodActualDimensionFactory.create(
        result_indicator_period=result_indicator_period)
    _create_test_narrative(
        activity,
        result_indicator_period.resultindicatorperiodactualcomment,
        resultindicatorperiodactualcomment_narrative_1)

    fss = FssFactory.create(activity=activity)
    FssForecastFactory.create(fss=fss)

    return activity
