# tasks.py
from iati_synchroniser.models import IatiXmlSource
from django_rq import job
import django_rq
import datetime


###############################
######## WORKER TASKS  ########
###############################

@job
def start_worker(queue_name, amount_of_workers):
    from rq import Queue, Connection, Worker
    from redis import Redis

    redis_conn = Redis()
    queue = Queue(queue_name, connection=redis_conn)

    amount_of_workers = int(amount_of_workers) + 1

    with Connection():
        workername = "oipa-" + queue_name + "-" + str(amount_of_workers)
        w = Worker(queue, workername)
        w.work()


@job
def advanced_start_worker():
    from rq import Queue, Connection, Worker
    from redis import Redis

    redis_conn = Redis()
    queue = Queue('default', connection=redis_conn)

    with Connection():
        w = Worker(queue)
        w.work()



###############################
#### TASK QUEUE MANAGEMENT ####
###############################

@job
def remove_duplicates_from_parser_queue():
    raise Exception("Not implemented yet")


###############################
######## PARSING TASKS ########
###############################

@job
def parse_all_existing_sources():
    for e in IatiXmlSource.objects.all():
        queue = django_rq.get_queue("parser")
        queue.enqueue(parse_source_by_url, args=(e.source_url,), timeout=7200)


@job
def get_new_sources_from_iati_api():
    from iati_synchroniser.dataset_syncer import DatasetSyncer
    ds = DatasetSyncer()
    ds.synchronize_with_iati_api(1)
    
    # Add parse_all_over_parse_interval job, to parse all new sources
    queue = django_rq.get_queue("parser")
    queue.enqueue(parse_all_over_parse_interval, timeout=7200)
    

@job
def parse_source_by_url(url):
    if IatiXmlSource.objects.filter(source_url=url).exists():
        xml_source = IatiXmlSource.objects.get(source_url=url)
        xml_source.process()



@job
def parse_all_not_parsed_in_x_days(days):
    for source in IatiXmlSource.objects.all():
        curdate = float(datetime.datetime.now().strftime('%s'))
        last_updated = float(source.date_updated.strftime('%s'))

        update_interval_time = 24 * 60 * 60 * int(days)

        if ((curdate - update_interval_time) > last_updated):
            queue = django_rq.get_queue("parser")
            queue.enqueue(parse_source_by_url, args=(source.source_url,), timeout=7200)

@job
def parse_all_over_parse_interval():
    for source in IatiXmlSource.objects.all():
        curdate = float(datetime.datetime.now().strftime('%s'))
        last_updated = float(source.date_updated.strftime('%s'))
        update_interval = source.update_interval

        if update_interval == "day":
            update_interval_time = 24 * 60 * 60
        if update_interval == "week":
            update_interval_time = 24 * 60 * 60 * 7
        if update_interval == "month":
            update_interval_time = 24 * 60 * 60 * 7 * 4.34
        if update_interval == "year":
            update_interval_time = 24 * 60 * 60 * 365

        if ((curdate - update_interval_time) > last_updated):
            source.save()


@job
def delete_source_by_id(id):
    if IatiXmlSource.objects.filter(id=id).exists():
        xml_source = IatiXmlSource.objects.get(id=id)
        xml_source.delete()

@job
def delete_sources_not_found_in_registry_in_x_days(days):
    if int(days) < 6:
        raise Exception("Bad idea to delete sources not found for only 5 days or less.")
    for source in IatiXmlSource.objects.all():
        curdate = float(datetime.datetime.now().strftime('%s'))
        if source.last_found_in_registry:
            last_found_in_registry = float(source.last_found_in_registry.strftime('%s'))

            update_interval_time = 24 * 60 * 60 * int(days)

            if ((curdate - update_interval_time) > last_found_in_registry):
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
######## GEODATA TASKS ########
###############################

@job
def update_all_geo_data():
    raise Exception("Not implemented yet")

@job
def update_all_city_data():
    raise Exception("Not implemented yet")

@job
def update_all_country_data():
    raise Exception("Not implemented yet")

@job
def update_all_region_data():
    raise Exception("Not implemented yet")

@job
def update_all_admin1_region_data():
    raise Exception("Not implemented yet")


###############################
######## INDICATOR TASKS ########
###############################

@job
def update_all_indicator_data():
    raise Exception("Not implemented yet")


###############################
######## CACHING TASKS ########
###############################

@job
def update_existing_api_call_caches():
    from cache.validator import Validator
    v = Validator()
    v.update_cache_calls()

@job
def cache_long_api_calls():
    from cache.validator import Validator
    v = Validator()
    v.update_response_times_and_add_to_cache()



def delete_task_from_queue(job_id):
    from rq import cancel_job
    from rq import Connection
    with Connection():
        cancel_job(job_id)

def delete_all_tasks_from_queue(queue_name):
    if queue_name == "failed":
        q = django_rq.get_failed_queue()
    elif queue_name == "parser":
        q = django_rq.get_queue("parser")
    else:
        q = django_rq.get_queue("default")

    while True:
        job = q.dequeue()
        if not job:
            break
        job.delete()