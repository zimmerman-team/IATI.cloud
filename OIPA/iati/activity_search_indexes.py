from datetime import datetime
from functools import partial

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist

from common.util import print_progress, setInterval
from iati.models import (
    Activity,
    ActivitySearch,
    ContactInfoDepartment,
    ContactInfoPersonName,
    ContactInfoJobTitle,
    ContactInfoMailingAddress,
    ContactInfoOrganisation,
    CountryBudgetItem,
    BudgetItemDescription,
    ResultTitle,
    ResultDescription,
    ResultIndicatorTitle,
    ResultIndicatorDescription,
    Conditions,
    DocumentLinkTitle
)
from iati.transaction.models import (
    TransactionDescription,
    TransactionProvider,
    TransactionReceiver
)

from iati_synchroniser.models import Publisher
from iati_organisation.models import Organisation, OrganisationName


# TODO: prefetches - 2016-01-07
def reindex_activity(activity):
    if hasattr(
        settings, 'FTS_ENABLED'
    ) and getattr(settings, 'FTS_ENABLED') is False:
        return

    try:
        activity_search = ActivitySearch.objects.get(activity=activity.id)
    except ObjectDoesNotExist:
        activity_search = ActivitySearch()

    # data prep
    title_text = []
    try:
        for narrative in activity.title.narratives.all():
            title_text.append(narrative.content)
    except ObjectDoesNotExist as e:
        pass

    description_text = []
    for description in activity.description_set.all():
        for narrative in description.narratives.all():
            description_text.append(narrative.content)

    reporting_org_text = []
    for reporting_org in activity.reporting_organisations.all():
        reporting_org_text.append(reporting_org.normalized_ref)
        for narrative in reporting_org.narratives.all():
            reporting_org_text.append(narrative.content)

    # The Publisher of the activity is a Reporting Organisation
    try:
        for narrative in activity.publisher.organisation.name.narratives.all():
            reporting_org_text.append(narrative.content)
    except (
        Publisher.DoesNotExist, Organisation.DoesNotExist,
        OrganisationName.DoesNotExist
    ):
        pass

    participating_org_text = []
    for participating_org in activity.participating_organisations.all():
        participating_org_text.append(participating_org.normalized_ref)
        for narrative in participating_org.narratives.all():
            participating_org_text.append(narrative.content)

    recipient_country_text = []
    for country in activity.recipient_country.all():
        recipient_country_text.append(country.code)
        recipient_country_text.append(country.name)

    recipient_region_text = []
    for region in activity.recipient_region.all():
        recipient_region_text.append(region.code)
        recipient_region_text.append(region.name)

    sector_text = []
    for sector in activity.sector.all():
        sector_text.append(sector.code)
        sector_text.append(sector.name)

    document_link_text = []
    for document_link in activity.documentlink_set.all():
        document_link_text.append(document_link.url)

        for category in document_link.categories.all():
            document_link_text.append(category.name)

        try:
            title = document_link.documentlinktitle
            for narrative in title.narratives.all():
                document_link_text.append(narrative.content)
        except DocumentLinkTitle.DoesNotExist as e:
            pass

    other_identifier_text = []
    for other_identifier in activity.otheridentifier_set.all():
        other_identifier_text.append(other_identifier.owner_ref)
        for narrative in other_identifier.narratives.all():
            other_identifier_text.append(narrative.content)

    contact_info_text = []
    for contact_info in activity.contactinfo_set.all():
        # iati-activities/iati-activity/contact-info/organisation/narrative
        try:
            organisation = ContactInfoOrganisation.objects.get(
                contact_info=contact_info
            )
            for narrative in organisation.narratives.all():
                contact_info_text.append(narrative.content)
        except ContactInfoOrganisation.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/contact-info/department/narrative
        try:
            for narrative in contact_info.department.narratives.all():
                contact_info_text.append(narrative.content)
        except ContactInfoDepartment.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/contact-info/person-name/narrative
        try:
            for narrative in contact_info.person_name.narratives.all():
                contact_info_text.append(narrative.content)
        except ContactInfoPersonName.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/contact-info/job-title/narrative
        try:
            for narrative in contact_info.job_title.narratives.all():
                contact_info_text.append(narrative.content)
        except ContactInfoJobTitle.DoesNotExist:
            pass

        # iati-activities/iati-activity/contact-info/mailing-address/narrative
        try:
            for narrative in contact_info.mailing_address.narratives.all():
                contact_info_text.append(narrative.content)
        except ContactInfoMailingAddress.DoesNotExist as e:
            pass

    location_text = []
    for location in activity.location_set.all():
        if location.ref:
            location_text.append(location.ref)

    # iati-activities/iati-activity/country-budget-items/budget-item/description/narrative
    country_budget_items_text = []
    try:
        for budget_item in activity.country_budget_items.budgetitem_set.all():
            try:
                for narrative in budget_item.description.narratives.all():
                    country_budget_items_text.append(narrative.content)
            except BudgetItemDescription.DoesNotExist as e:
                pass
    except CountryBudgetItem.DoesNotExist as e:
        pass

    # iati-activities/iati-activity/policy-marker/narrative
    policy_marker_text = []
    for activity_policy_marker in activity.activitypolicymarker_set.all():
        for narrative in activity_policy_marker.narratives.all():
            policy_marker_text.append(narrative.content)

    transaction_text = []
    for transaction in activity.transaction_set.all():
        if transaction.ref:
            transaction_text.append(transaction.ref)

        # iati-activities/iati-activity/transaction/description/narrative
        try:
            for narrative in transaction.description.narratives.all():
                transaction_text.append(narrative.content)
        except TransactionDescription.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/transaction/provider-org/
        try:
            transaction_text.append(transaction.provider_organisation.ref)
            for narrative in transaction.provider_organisation.narratives.all():
                transaction_text.append(narrative.content)
        except TransactionProvider.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/transaction/receiver-org/
        try:
            transaction_text.append(transaction.receiver_organisation.ref)
            for narrative in transaction.receiver_organisation.narratives.all():  # NOQA: E501
                transaction_text.append(narrative.content)
        except TransactionReceiver.DoesNotExist as e:
            pass

    related_activity_text = []
    for related_activity in activity.relatedactivity_set.all():
        related_activity_text.append(related_activity.ref)

    # iati-activities/iati-activity/conditions
    conditions_text = []
    try:
        for condition in activity.conditions.condition_set.all():
            for narrative in condition.narratives.all():
                conditions_text.append(narrative.content)
    except Conditions.DoesNotExist as e:
        pass

    result_text = []
    for result in activity.result_set.all():
        # iati-activities/iati-activity/result/title/narrative
        try:
            for narrative in result.resulttitle.narratives.all():
                result_text.append(narrative.content)
        except ResultTitle.DoesNotExist as e:
            pass

        # iati-activities/iati-activity/result/description/narrative
        try:
            for narrative in result.resultdescription.narratives.all():
                result_text.append(narrative.content)
        except ResultDescription.DoesNotExist as e:
            pass

        for result_indicator in result.resultindicator_set.all():
            # iati-activities/iati-activity/result/indicator/title/narrative
            try:
                for narrative in \
                        result_indicator.resultindicatortitle.narratives.all():
                    result_text.append(narrative.content)
            except ResultIndicatorTitle.DoesNotExist as e:
                pass

            # iati-activities/iati-activity/result/indicator/description/narrative
            try:
                for narrative in result_indicator.resultindicatordescription.narratives.all():  # NOQA: E501
                    result_text.append(narrative.content)
            except ResultIndicatorDescription.DoesNotExist as e:
                pass

            for result_indicator_period in result_indicator.resultindicatorperiod_set.all():  # NOQA: E501
                # iati-activities/iati-activity/result/indicator/period/target/comment/narrative
                for target in result_indicator_period.targets.all():
                    for target_comment in target.resultindicatorperiodtargetcomment_set.all():  # NOQA: E501
                        for narrative in target_comment.narratives.all():
                            result_text.append(narrative.content)

                # iati-activities/iati-activity/result/indicator/period/actual/comment/narrative
                for actual in result_indicator_period.actuals.all():
                    for actual_comment in actual.resultindicatorperiodactualcomment_set.all():  # NOQA: E501
                        for narrative in actual_comment.narratives.all():
                            result_text.append(narrative.content)

    activity_search.activity = activity
    activity_search.iati_identifier = activity.iati_identifier
    activity_search.title = " ".join(title_text)
    activity_search.description = " ".join(description_text)
    activity_search.reporting_org = " ".join(reporting_org_text)
    activity_search.participating_org = " ".join(participating_org_text)
    activity_search.recipient_country = " ".join(recipient_country_text)
    activity_search.recipient_region = " ".join(recipient_region_text)
    activity_search.sector = " ".join(sector_text)
    activity_search.document_link = " ".join(document_link_text)
    activity_search.other_identifier = " ".join(other_identifier_text)
    activity_search.contact_info = " ".join(contact_info_text)
    activity_search.location = " ".join(location_text)
    activity_search.country_budget_items = " ".join(country_budget_items_text)
    activity_search.transaction = " ".join(transaction_text)
    activity_search.policy_marker = " ".join(policy_marker_text)
    activity_search.related_activity = " ".join(related_activity_text)
    activity_search.conditions = " ".join(conditions_text)
    activity_search.result = " ".join(result_text)

    _config = 'english'

    combined_vector = SearchVector(
        'iati_identifier',
        config=_config
    ) + SearchVector(
        'title',
        config=_config
    ) + SearchVector(
        'description',
        config=_config
    ) + SearchVector(
        'reporting_org',
        config=_config
    ) + SearchVector(
        'participating_org',
        config=_config
    ) + SearchVector(
        'recipient_country',
        config=_config
    ) + SearchVector(
        'recipient_region',
        config=_config
    ) + SearchVector(
        'sector',
        config=_config
    ) + SearchVector(
        'document_link',
        config=_config
    ) + SearchVector(
        'other_identifier',
        config=_config
    ) + SearchVector(
        'contact_info',
        config=_config
    ) + SearchVector(
        'location',
        config=_config
    ) + SearchVector(
        'country_budget_items',
        config=_config
    ) + SearchVector(
        'policy_marker',
        config=_config
    ) + SearchVector(
        'transaction',

        config=_config
    )+ SearchVector(
        'related_activity',
        config=_config
    ) + SearchVector(
        'conditions',
        config=_config
    ) + SearchVector(
        'result',
        config=_config
    )

    activity_search.last_reindexed = datetime.now()
    activity_search.save()
    ActivitySearch.objects.filter(id=activity_search.id).update(
        search_vector_text=combined_vector)


def reindex_all_activities():

    progress = {
        'offset': 0,
        'count': Activity.objects.all().count()
    }

    setInterval(partial(print_progress, progress), 10)

    for activity in Activity.objects.all().iterator():
        reindex_activity(activity)
        progress['offset'] += 1


def reindex_activity_by_source(dataset_id):
    activities = Activity.objects.all().filter(dataset__id=dataset_id)
    for activity in activities:
        reindex_activity(activity)
