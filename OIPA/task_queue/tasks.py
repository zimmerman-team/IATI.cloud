import datetime
import hashlib
import os
import time

import django_rq
import fulltext
import requests
from django.conf import settings
from django.core.cache import caches
from django_rq import job
from redis import Redis
from rest_framework_extensions.settings import extensions_api_settings
from rq import Worker
from rq.job import Job

from api.export.serializers import ActivityXMLSerializer
from api.renderers import XMLRenderer
from common.download_file import DownloadFile, hash_file
from iati.activity_aggregation_calculation import (
    ActivityAggregationCalculation
)
from iati.models import Activity, Budget, Document, DocumentLink, Result
from iati.transaction.models import Transaction
from iati_synchroniser.models import Dataset, DatasetNote
from solr.activity.tasks import ActivityTaskIndexing
from solr.activity.tasks import solr as solr_activity
from solr.budget.tasks import solr as solr_budget
from solr.datasetnote.tasks import DatasetNoteTaskIndexing
from solr.datasetnote.tasks import solr as solr_dataset_note
from solr.result.tasks import solr as solr_result
from solr.transaction.tasks import solr as solr_transaction

redis_conn = Redis.from_url(settings.RQ_REDIS_URL)


###############################
#### TASK QUEUE MANAGEMENT ####  # NOQA: E266
###############################


def remove_all_api_caches():
    """
    Call this function after the API data has been changed,
    to remove all cached of the API data

    TODO: remove just for a specific of the API data which has been changed
    """
    api_caches = caches[extensions_api_settings.DEFAULT_USE_CACHE]
    api_caches.clear()


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
######## PARSING TASKS ########  # NOQA: E266
###############################

@job
def get_new_sources_from_iati_api():
    from django.core import management
    management.call_command('get_new_sources_from_iati_registry', verbosity=0)


@job
def get_new_sources_from_iati_api_and_download():
    from django.core import management
    management.call_command(
        'get_new_sources_from_iati_registry_and_download',
        verbosity=0
    )


@job
def add_new_sources_from_registry_and_parse_all():
    queue = django_rq.get_queue("default")
    queue.enqueue(get_new_sources_from_iati_api)
    queue.enqueue(parse_all_existing_sources)


@job
def perform_initial_tasks():
    # TODO: this guy is not used anymore, because the second task
    # (get_new_sources_from_iati_api) needed "code-list Version" from the
    # first task, so this task can not run together in the same time.
    queue = django_rq.get_queue("default")
    queue.enqueue(update_iati_codelists)
    queue.enqueue(get_new_sources_from_iati_api)


@job
def force_parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in Dataset.objects.all().filter(filetype=2):
        queue.enqueue(force_parse_source_by_id, args=(e.id,), timeout=14400)

    for e in Dataset.objects.all().filter(filetype=1):
        queue.enqueue(force_parse_source_by_id, args=(e.id,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def parse_all_existing_sources():
    """
    First parse all organisation sources, then all activity sources
    """
    queue = django_rq.get_queue("parser")

    for e in Dataset.objects.all().filter(filetype=2):
        queue.enqueue(parse_source_by_id, args=(e.id,), timeout=14400)

    for e in Dataset.objects.all().filter(filetype=1):
        queue.enqueue(parse_source_by_id, args=(e.id,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def parse_all_sources_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in Dataset.objects.filter(publisher__publisher_iati_id=org_ref):
        queue.enqueue(parse_source_by_id, args=(e.id,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def force_parse_by_publisher_ref(org_ref):
    queue = django_rq.get_queue("parser")
    for e in Dataset.objects.filter(publisher__publisher_iati_id=org_ref):
        queue.enqueue(force_parse_source_by_id, args=(e.id,), timeout=14400)

    if settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def force_parse_source_by_url(url, update_searchable=False):
    if Dataset.objects.filter(source_url=url).exists():
        xml_source = Dataset.objects.get(source_url=url)
        xml_source.process(force_reparse=True)

    queue = django_rq.get_queue("parser")
    if update_searchable and settings.ROOT_ORGANISATIONS:
        queue.enqueue(start_searchable_activities_task, args=(0,), timeout=300)


@job
def force_parse_source_by_id(source_id, update_searchable=False):
    try:
        xml_source = Dataset.objects.get(pk=source_id)
        xml_source.process(force_reparse=True)

        queue = django_rq.get_queue("parser")
        if update_searchable and settings.ROOT_ORGANISATIONS:
            queue.enqueue(start_searchable_activities_task,
                          args=(0,), timeout=300)

    except Dataset.DoesNotExist:
        return False


@job
def parse_source_by_url(url):
    if Dataset.objects.filter(source_url=url).exists():
        xml_source = Dataset.objects.get(source_url=url)
        xml_source.process()


@job
def parse_source_by_id(source_id):
    try:
        xml_source = Dataset.objects.get(pk=source_id)
        xml_source.process()

    except Dataset.DoesNotExist:
        return False


@job
def calculate_activity_aggregations_per_source(source_ref):
    aac = ActivityAggregationCalculation()
    aac.parse_activity_aggregations_by_source(source_ref)


@job
def delete_source_by_id(source_id):
    try:
        Dataset.objects.get(pk=source_id).delete()

    except Dataset.DoesNotExist:
        return False


@job
def delete_sources_not_found_in_registry_in_x_days(days):
    if int(days) < 6:
        raise Exception(
            "The task queue only allows deletion of sources when not found \
                for +5 days")

    for source in Dataset.objects.all():
        current_date = float(datetime.datetime.now().strftime('%s'))
        if source.last_found_in_registry:
            last_found_in_registry = float(
                source.last_found_in_registry.strftime('%s'))
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
#### IATI MANAGEMENT TASKS ####  # NOQA: E266
###############################

@job
def update_iati_codelists():
    from iati_synchroniser.codelist_importer import CodeListImporter
    syncer = CodeListImporter()
    syncer.synchronise_with_codelists()


@job
def find_replace_source_url(find_url, replace_url):
    for source in Dataset.objects.filter(source_url__icontains=find_url):
        source.source_url = source.source_url.replace(find_url, replace_url)
        source.save()


########################
#### INTERNAL TASKS ####  # NOQA: E266
########################


@job
def export_publisher_activities(publisher_id):
    queryset = Activity.objects.all().filter(
        ready_to_publish=True,
        publisher_id=publisher_id
    )

    serializer = ActivityXMLSerializer(queryset, many=True)

    xml_renderer = XMLRenderer()
    xml = xml_renderer.render(serializer.data)

    return xml


#############################
#### EXCHANGE RATE TASKS ####  # NOQA: E266
#############################

@job
def update_exchange_rates():
    # XXX: no such module exists!
    from currency_convert.imf_rate_parser import RateParser
    r = RateParser()
    r.update_rates(force=False)


@job
def force_update_exchange_rates():
    # XXX: no such module exists!
    from currency_convert.imf_rate_parser import RateParser
    r = RateParser()
    r.update_rates(force=True)


###############################
######## GEODATA TASKS ########  # NOQA: E266
###############################

@job
def update_all_geo_data():
    queue = django_rq.get_queue("default")
    queue.enqueue(update_region_data)
    queue.enqueue(update_country_data)
    queue.enqueue(update_adm1_region_data)


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


#############################################
######## SEARCHABLE ACTIVITIES TASKS ########  # NOQA: E266
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
                    if ('start_searchable_activities_task'
                            not in current_job.description):
                        has_other_jobs = True
                    if ('update_searchable_activities'
                            in current_job.description):
                        already_running_update = True

    if already_running_update:
        # update_searchable_activities already running or other
        # start_searchable_activities_task running, invalidate task
        pass
    elif not has_other_jobs:
        queue.enqueue(update_searchable_activities)
    elif counter > 180:
        raise Exception(
            "Waited for 30 min, still jobs runnings so invalidating this task. \
                    If this happens please contact OIPA devs!")
    else:
        counter += 1
        time.sleep(120)
        queue.enqueue(start_searchable_activities_task,
                      args=(counter,), timeout=300)


@job
def update_searchable_activities():
    from django.core import management
    management.call_command('set_searchable_activities', verbosity=0)


#############################################
############# Docstore TASKS ################  # NOQA: E266
#############################################


@job
def collect_files():
    queue = django_rq.get_queue("document_collector")
    for d in DocumentLink.objects.all():
        queue.enqueue(download_file, args=(d,))


@job
def download_file(d):
    document_link = DocumentLink.objects.get(pk=d.pk)
    doc, created = Document.objects.get_or_create(document_link=document_link)
    extensions = (
        'doc',
        'pdf',
        'docx',
        'xls',
    )
    document_content = ''

    if d.url:
        '''Define the working Directory and saving Path'''
        wk_dir = os.path.dirname(os.path.realpath('__file__'))
        save_path = wk_dir + "/docstore/"

        '''Unshort URLs and get file name'''
        r = requests.head(d.url, allow_redirects=True)
        if d.url != r.url:
            long_url = r.url
        else:
            long_url = d.url
        doc.long_url = long_url
        local_filename = long_url.split('/')[-1]
        doc.document_name = local_filename

        '''Verify if the the URL is containing a file and authorize download'''
        file_extension = local_filename.split('.')[-1].lower()
        save_name = str(d.pk) + '.' + file_extension
        document_path = save_path + save_name
        is_downloaded = False

        if file_extension in extensions:
            if created or (not created and not doc.is_downloaded):
                doc.url_is_valid = True
                downloader = DownloadFile(long_url, document_path)
                try:
                    is_downloaded = downloader.download()
                    doc.is_downloaded = is_downloaded
                except Exception as e:
                    # print str(e)
                    pass

                '''Get Text from file and save document'''
                if is_downloaded:
                    doc.long_url_hash = hashlib.md5(long_url).hexdigest()
                    doc.file_hash = hash_file(document_path)
                    document_content = fulltext.get(
                        save_path + save_name, '< no content >')
                    doc.document_content = document_content

            if (not created and doc.is_downloaded):
                '''prepare the updated file storage with the new name \
                        <update.timestamp.id.extention'''
                ts = time.time()
                document_path_update = save_path + \
                    "update." + str(ts) + "." + save_name
                downloader = DownloadFile(long_url, document_path_update)
                try:
                    is_downloaded = downloader.download()
                except Exception as e:
                    # print str(e)
                    pass
                '''hash the downloaded file and it long url'''
                if is_downloaded:
                    long_url_hash = hashlib.md5(long_url).hexdigest()
                    file_hash = hash_file(document_path_update)
                '''if file hash or url hash id different, parse the content '
                of the file'''
                if is_downloaded and long_url_hash != '' and (
                        doc.long_url_hash != long_url_hash
                        or doc.file_hash != file_hash):
                    doc.document_or_long_url_changed = True
                    doc.long_url_hash = long_url_hash
                    doc.file_hash = file_hash
                    document_content = fulltext.get(
                        document_path_update, '< no content >')
                    doc.document_content = document_content
                else:
                    '''delete the updated file. This file is empty'''
                    os.remove(document_path_update)
    try:
        doc.save()
    except Exception as e:
        # print str(e)
        doc.document_content = document_content.decode("latin-1")
        doc.save()


@job
def update_activity_count():
    for dataset in Dataset.objects.all():
        dataset.update_activities_count()


@job
def synchronize_solr_indexing():
    queue = django_rq.get_queue('solr')
    # Budget
    list_budget_id = list(
        Budget.objects.all().values_list('id', flat=True)
    )
    budget_hits = solr_budget.search(q='*:*', fl='id').hits
    budget_docs = solr_budget.search(
        q='*:*',  fl='id', rows=budget_hits
    ).docs
    list_budget_doc_id = [
        int(budget_doc['id']) for budget_doc in budget_docs
    ]
    for ids in divide_delete_ids(list_budget_id, list_budget_doc_id):
        delete_multiple_rows_budget_in_solr(ids)

    # Result
    list_result_id = list(
        Result.objects.all().values_list('id', flat=True)
    )
    result_hits = solr_result.search(q='*:*', fl='id').hits
    result_docs = solr_result.search(
        q='*:*', fl='id', rows=result_hits
    ).docs
    list_result_doc_id = [
        int(result_doc['id']) for result_doc in result_docs
    ]
    for ids in divide_delete_ids(list_result_id, list_result_doc_id):
        delete_multiple_rows_result_in_solr(ids)

    # Transaction
    list_transaction_id = list(
        Transaction.objects.all().values_list('id', flat=True)
    )
    transaction_hits = solr_transaction.search(q='*:*', fl='id').hits
    transaction_docs = solr_transaction.search(
        q='*:*', fl='id', rows=transaction_hits
    ).docs
    list_transaction_doc_id = [
        int(transaction_doc['id']) for transaction_doc in transaction_docs
    ]
    for ids in divide_delete_ids(list_transaction_id, list_transaction_doc_id):
        delete_multiple_rows_transaction_in_solr(ids)

    # Activity
    list_activity_id = list(
        Activity.objects.all().values_list('id', flat=True)
    )
    activity_hits = solr_activity.search(q='*:*', fl='id').hits
    activity_docs = solr_activity.search(
        q='*:*', fl='id', rows=activity_hits
    ).docs
    list_activity_doc_id = [
        int(activity_doc['id']) for activity_doc in activity_docs
    ]
    for ids in divide_delete_ids(list_activity_id, list_activity_doc_id):
        delete_multiple_rows_activiy_in_solr(ids)

    for activity_id in (
        list(set(list_activity_id) - set(list_activity_doc_id))
    ):
        queue.enqueue(add_activity_to_solr, args=(activity_id,))

    """# Dataset Note
    list_dataset_note_id = list(
        DatasetNote.objects.all().values_list('id', flat=True)
    )
    dataset_note_hits = solr_dataset_note.search(q='*:*', fl='id').hits
    dataset_note_docs = solr_dataset_note.search(
        q='*:*', fl='id', rows=dataset_note_hits
    ).docs
    list_dataset_note_doc_id = [
        int(dataset_note_doc['id']) for dataset_note_doc in dataset_note_docs
    ]
    for ids in divide_delete_ids(
            list_dataset_note_id,
            list_dataset_note_doc_id
    ):
        delete_multiple_rows_dataset_note_in_solr(ids)

    for dataset_note_id in (
        list(set(list_dataset_note_id) - set(list_dataset_note_doc_id))
    ):
        queue.enqueue(add_dataset_note_to_solr, args=(dataset_note_id,))"""


def divide_delete_ids(list_ids, list_solr_ids, start=0, end=1000, inc=1000):
    ids_to_delete = list(
        set(list_solr_ids) - set(list_ids)
    )
    ids = ids_to_delete[start:end]
    result = []
    while ids:
        result.append(ids)
        start += inc
        end += inc
        ids = ids_to_delete[start:end]

    return result


@job
def add_activity_to_solr(activity_id):
    try:
        ActivityTaskIndexing(
            instance=Activity.objects.get(id=activity_id),
            related=True
        ).run()
    except Activity.DoesNotExist:
        pass


@job
def delete_dataset_note_in_solr(dataset_note_id):
    solr_dataset_note.delete(q='id:{id}'.format(id=dataset_note_id))


@job
def delete_multiple_rows_activiy_in_solr(ids):
    solr_activity.delete(
        q='id:({ids})'.format(ids=' OR '.join(str(i) for i in ids))
    )


@job
def delete_multiple_rows_budget_in_solr(ids):
    solr_budget.delete(
        q='id:({ids})'.format(ids=' OR '.join(str(i) for i in ids))
    )


@job
def delete_multiple_rows_transaction_in_solr(ids):
    solr_transaction.delete(
        q='id:({ids})'.format(ids=' OR '.join(str(i) for i in ids))
    )


@job
def delete_multiple_rows_result_in_solr(ids):
    solr_result.delete(
        q='id:({ids})'.format(ids=' OR '.join(str(i) for i in ids))
    )


@job
def delete_multiple_rows_dataset_note_in_solr(ids):
    solr_dataset_note.delete(
        q='id:({ids})'.format(ids=' OR '.join(str(i) for i in ids))
    )


@job
def add_dataset_note_to_solr(dataset_note_id):
    try:
        DatasetNoteTaskIndexing(
            instance=DatasetNote.objects.get(id=dataset_note_id),
            related=True
        ).run()
    except DatasetNote.DoesNotExist:
        pass
