from iati.models import Activity, ActivitySearch
from datetime import datetime
from functools import partial

from django.core.exceptions import ObjectDoesNotExist
from common.util import setInterval, print_progress

import sys
import traceback

from django.conf import settings
from django.contrib.postgres.search import SearchVector


# TODO: prefetches - 2016-01-07
def reindex_activity(activity):
    if hasattr(settings, 'FTS_ENABLED') and getattr(settings, 'FTS_ENABLED') == False:
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
        except ObjectDoesNotExist as e:
            pass

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

    text = " ".join([
        activity_search.iati_identifier,
        activity_search.title,
        activity_search.description,
        activity_search.reporting_org,
        activity_search.participating_org,
        activity_search.recipient_country,
        activity_search.recipient_region,
        activity_search.sector,
        activity_search.document_link,
    ])

    combined_vector = SearchVector('iati_identifier',
                                   config='english') + SearchVector('title',
                                                                    config='english') + SearchVector('description',
                                                                                                     config='english') + SearchVector('reporting_org',
                                                                                                                                      config='english') + SearchVector('participating_org',
                                                                                                                                                                       config='english') + SearchVector('recipient_country',
                                                                                                                                                                                                        config='english') + SearchVector('recipient_region',
                                                                                                                                                                                                                                         config='english') + SearchVector('sector',
                                                                                                                                                                                                                                                                          config='english') + SearchVector('document_link',
                                                                                                                                                                                                                                                                                                           config='english')

    # activity_search.search_vector_text = combined_vector

    activity_search.last_reindexed = datetime.now()
    activity_search.save()
    ActivitySearch.objects.filter(id=activity_search.id).update(search_vector_text=combined_vector)


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
