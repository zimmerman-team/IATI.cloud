from iati_synchroniser.models import IatiXmlSource
from iati.activity_aggregation_calculation import ActivityAggregationCalculation
from django_rq import job
import django_rq
import datetime
from rq import Queue, Connection, Worker
from rq.job import Job
from redis import Redis
from django.conf import settings


redis_conn = Redis()

###############################
######## WORKER TASKS  ########
###############################

@job
def start_worker(queue_name):
    queue = Queue(queue_name, connection=redis_conn)
    amount_of_workers = 1

    workers = Worker.all(connection=redis_conn)

    for w in workers:
        if w.queues[0].name == queue_name:
            amount_of_workers += 1

    workername = "oipa-" + queue_name + "-" + str(amount_of_workers)
    w = Worker(queue, workername, connection=redis_conn)
    w.work()


@job
def stop_worker(queue_name):
    queue = Queue(queue_name, connection=redis_conn)
    workers = Worker.all(connection=redis_conn)
    last_worker_index = len(workers) - 1
    worker[last_worker_index].request_stop()


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
def force_parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in IatiXmlSource.objects.all().filter(type=2):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,), timeout=14400)

    for e in IatiXmlSource.objects.all().filter(type=1):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(update_searchable_activities, timeout=14400)


@job
def add_new_sources_from_registry_and_parse_all():
    queue = django_rq.get_queue("default")
    queue.enqueue(get_new_sources_from_iati_api, timeout=14400)
    queue.enqueue(parse_all_existing_sources, timeout=14400)


@job
def parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in IatiXmlSource.objects.all().filter(type=2):
        queue.enqueue(parse_source_by_url, args=(e.source_url,), timeout=14400)

    for e in IatiXmlSource.objects.all().filter(type=1):
        queue.enqueue(parse_source_by_url, args=(e.source_url,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(update_searchable_activities, timeout=14400)


@job
def parse_all_sources_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in IatiXmlSource.objects.filter(publisher__org_id=org_ref):
        queue.enqueue(parse_source_by_url, args=(e.source_url,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(update_searchable_activities, timeout=14400)


@job
def force_parse_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in IatiXmlSource.objects.filter(publisher__org_id=org_ref):
        queue.enqueue(force_parse_source_by_url, args=(e.source_url,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(update_searchable_activities, timeout=14400)


@job
def get_new_sources_from_iati_api():
    from django.core import management
    management.call_command('get_new_sources_from_iati_registry', verbosity=0, interactive=False)


@job
def force_parse_source_by_url(url):
    if IatiXmlSource.objects.filter(source_url=url).exists():
        xml_source = IatiXmlSource.objects.get(source_url=url)
        xml_source.process(force_reparse=True)


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
                queue.enqueue(delete_source_by_id, args=(source.id,), timeout=7200)

        else:
            if not source.added_manually:
                # Old source, delete
                queue = django_rq.get_queue("parser")
                queue.enqueue(delete_source_by_id, args=(source.id,), timeout=7200)


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


###############################
######## SEARCHABLE ACTIVITIES TASKS ########
###############################

@job
def update_searchable_activities():
    import time
    import django_rq
    from django.core import management

    counter = 0

    workers = Worker.all(connection=redis_conn)

    in_loop = True

    while in_loop:
        has_other_jobs = False
        
        for w in workers:
            if len(w.queues):
                if w.queues[0].name == "parser":
                    current_job = w.get_current_job()
                    if current_job and current_job.description != 'task_queue.tasks.update_searchable_activities()':
                        has_other_jobs = True
        
        if not has_other_jobs:
            management.call_command('set_searchable_activities', verbosity=0, interactive=False)
            in_loop = False
        elif counter > 2:
            # add new task to prevent timeout
            queue = django_rq.get_queue('parser')
            queue.enqueue(update_searchable_activities, timeout=14400)
            in_loop = False

        else:
            counter += 1
            time.sleep(180)

