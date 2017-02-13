from iati.models import Activity, ActivitySearch
from datetime import datetime
from functools import partial

from django.core.exceptions import ObjectDoesNotExist
from common.util import setInterval, print_progress

import sys, traceback

from django.conf import settings


# TODO: prefetches - 2016-01-07
def reindex_activity(activity):
    if getattr(settings, 'FTS_ENABLED') == False:
        return

    try:
        activity_search = ActivitySearch.objects.get(activity=activity.id)
    except ObjectDoesNotExist:
        activity_search = ActivitySearch()

    activity_search.activity = activity

    from iati.models import DescriptionType

    try:
        activity_search.iati_identifier = activity.iati_identifier

        title_text = []
        for narrative in activity.title.narratives.all():
            title_text.append(narrative.content)
        activity_search.title = " ".join(title_text)

        description_text = []
        for description in activity.description_set.all():
            for narrative in description.narratives.all():
                description_text.append(narrative.content)
        activity_search.description = " ".join(description_text)

        reporting_org_text = []
        for reporting_org in activity.reporting_organisations.all():
            reporting_org_text.append(reporting_org.normalized_ref)
            for narrative in reporting_org.narratives.all():
                reporting_org_text.append(narrative.content)
        activity_search.reporting_org = " ".join(reporting_org_text)

        participating_org_text = []
        for participating_org in activity.participating_organisations.all():
            participating_org_text.append(participating_org.normalized_ref)
            for narrative in participating_org.narratives.all():
                participating_org_text.append(narrative.content)
        activity_search.participating_org = " ".join(participating_org_text)

        recipient_country_text = []
        for country in activity.recipient_country.all():
            recipient_country_text.append(country.code)
            recipient_country_text.append(country.name)
        activity_search.recipient_country = " ".join(recipient_country_text)

        recipient_region_text = []
        for region in activity.recipient_region.all():
            recipient_region_text.append(region.code)
            recipient_region_text.append(region.name)
        activity_search.recipient_region = " ".join(recipient_region_text)

        sector_text = []
        for sector in activity.sector.all():
            sector_text.append(sector.code)
            sector_text.append(sector.name)
        activity_search.sector = " ".join(sector_text)

        document_link_text = []
        for document_link in activity.documentlink_set.all():
            document_link_text.append(document_link.url)

            for category in document_link.categories.all():
                document_link_text.append(category.name)

            title = document_link.documentlinktitle
            for narrative in title.narratives.all():
                document_link_text.append(narrative.content)

        activity_search.document_link = " ".join(document_link_text)

        activity_search.text = " ".join([
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

        activity_search.last_reindexed = datetime.now()
        print('saving...')
        activity_search.save()

        print('saved...')

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print("Building ft indexes for {id} raises: {e}".format(id=activity.id, e=e.message))


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
