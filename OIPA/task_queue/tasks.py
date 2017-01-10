from iati_synchroniser.models import IatiXmlSource
from iati.activity_aggregation_calculation import ActivityAggregationCalculation
from django_rq import job
import django_rq
import datetime
from rq import Queue, Connection, Worker
from rq.job import Job
from redis import Redis
from django.conf import settings
import time


redis_conn = Redis()


###############################
#### TASK QUEUE MANAGEMENT ####
###############################


@job
def remove_duplicates_from_parser_queue():
    raise Exception("Not implemented yet")


def delete_task_from_queue(job_id):
    Job.fetch(job_id, connection=redis_conn).delete()


def delete_all_tasks_from_queue(queue_name):

    if queue_name == "failed":
        q = django_rq.get_failed_queue()
    elif queue_name == "parser":
        q = django_rq.get_queue("parser")
    else:
        q = django_rq.get_queue("default")

    while True:
        current_job = q.dequeue()
        if not current_job:
            break
        current_job.delete()


###############################
######## PARSING TASKS ########
###############################

@job
def get_new_sources_from_iati_api():
    from django.core import management
    management.call_command('get_new_sources_from_iati_registry', verbosity=0, interactive=False)


@job
def add_new_sources_from_registry_and_parse_all():
    queue = django_rq.get_queue("default")
    queue.enqueue(get_new_sources_from_iati_api)
    queue.enqueue(parse_all_existing_sources)


@job
def force_parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in IatiXmlSource.objects.all().filter(type=2):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,))

    for e in IatiXmlSource.objects.all().filter(type=1):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,))

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in IatiXmlSource.objects.all().filter(type=2):
        queue.enqueue(parse_source_by_url, args=(e.source_url,))

    for e in IatiXmlSource.objects.all().filter(type=1):
        queue.enqueue(parse_source_by_url, args=(e.source_url,))

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def parse_all_sources_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in IatiXmlSource.objects.filter(publisher__org_id=org_ref):
        queue.enqueue(parse_source_by_url, args=(e.source_url,))

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def force_parse_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in IatiXmlSource.objects.filter(publisher__org_id=org_ref):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,))

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def force_parse_source_by_url(url, update_searchable=False):
    if IatiXmlSource.objects.filter(source_url=url).exists():
        xml_source = IatiXmlSource.objects.get(source_url=url)
        xml_source.process(force_reparse=True)

    queue = django_rq.get_queue("parser")
    if update_searchable and settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def parse_source_by_url(url):
    if IatiXmlSource.objects.filter(source_url=url).exists():
        xml_source = IatiXmlSource.objects.get(source_url=url)
        xml_source.process()


@job
def calculate_activity_aggregations_per_source(source_ref):
    aac = ActivityAggregationCalculation()
    aac.parse_activity_aggregations_by_source(source_ref)


@job
def delete_source_by_id(source_id):
    try:
        IatiXmlSource.objects.get(id=source_id).delete()
    except IatiXmlSource.DoesNotExist:
        return False


@job
def delete_sources_not_found_in_registry_in_x_days(days):

    if int(days) < 6:
        raise Exception("The task queue only allows deletion of sources when not found for +5 days")

    for source in IatiXmlSource.objects.all():
        current_date = float(datetime.datetime.now().strftime('%s'))
        if source.last_found_in_registry:
            last_found_in_registry = float(source.last_found_in_registry.strftime('%s'))
            update_interval_time = 24 * 60 * 60 * int(days)

            if (current_date - update_interval_time) > last_found_in_registry:
                queue = django_rq.get_queue("parser")
                queue.enqueue(delete_source_by_id, args=(source.id,))

        else:
            if not source.added_manually:
                # Old source, delete
                queue = django_rq.get_queue("parser")
                queue.enqueue(delete_source_by_id, args=(source.id,))


###############################
#### IATI MANAGEMENT TASKS ####
###############################

@job
def update_iati_codelists():
    from iati_synchroniser.codelist_importer import CodeListImporter
    syncer = CodeListImporter()
    syncer.synchronise_with_codelists()


###############################
#### EXCHANGE RATE TASKS ####
###############################

@job
def update_exchange_rates():
    from currency_convert.imf_rate_parser import RateParser
    r = RateParser()
    r.update_rates(force=False)


@job
def force_update_exchange_rates():
    from currency_convert.imf_rate_parser import RateParser
    r = RateParser()
    r.update_rates(force=True)

###############################
######## GEODATA TASKS ########
###############################

@job
def update_all_geo_data():
    queue = django_rq.get_queue("default")
    queue.enqueue(update_region_data)
    queue.enqueue(update_country_data)
    queue.enqueue(update_adm1_region_data)
    queue.enqueue(update_city_data)


@job
def update_region_data():
    from geodata.importer.region import RegionImport
    ri = RegionImport()
    ri.update_region_center()


@job
def update_country_data():
    from geodata.importer.country import CountryImport
    ci = CountryImport()
    ci.update_country_center()
    ci.update_polygon()
    ci.update_regions()


@job
def update_adm1_region_data():
    from geodata.importer.admin1region import Adm1RegionImport
    ai = Adm1RegionImport()
    ai.update_from_json()


@job
def update_city_data():
    from geodata.importer.city import CityImport
    ci = CityImport()
    ci.update_cities()


#############################################
######## SEARCHABLE ACTIVITIES TASKS ########
#############################################


@job
def wait_10():
    time.sleep(10)


@job
def wait_120():
    time.sleep(120)


@job
def wait_300():
    time.sleep(300)


@job
def start_searchable_activities_task(counter=0):
    workers = Worker.all(connection=redis_conn)
    queue = django_rq.get_queue("parser")

    has_other_jobs = False
    already_running_update = False
    
    for w in workers:
        if len(w.queues):
            if w.queues[0].name == "parser":
                current_job = w.get_current_job()
                if current_job:
                    if 'start_searchable_activities_task' not in current_job.description:
                        has_other_jobs = True
                    if 'update_searchable_activities' in current_job.description:
                        already_running_update = True

    if already_running_update:
        # update_searchable_activities already running or other start_searchable_activities_task running, invalidate task
        pass
    elif not has_other_jobs:
        queue.enqueue(update_searchable_activities)
    elif counter > 180:
        raise Exception("Waited for 30 min, still jobs runnings so invalidating this task. If this happens please contact OIPA devs!")
    else:
        counter += 1
        time.sleep(120)
        queue.enqueue(start_searchable_activities_task, args=(counter,), timeout=300)


@job
def update_searchable_activities():
    from django.core import management
    management.call_command('set_searchable_activities', verbosity=0, interactive=False)


