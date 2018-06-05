import json

import django_rq
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django_rq import get_connection
from rq import Worker, get_failed_queue, requeue_job
from rq.exceptions import NoSuchJobError
from rq.job import Job
from rq.registry import FinishedJobRegistry
from rq_scheduler import Scheduler

from task_queue import tasks


# PARSE TASKS
@staff_member_required
def add_task(request):
    task = request.GET.get('task')
    parameters = request.GET.get('parameters')
    parameters2 = request.GET.get('parameters2')
    queue_to_be_added_to = request.GET.get('queue')
    queue = django_rq.get_queue(queue_to_be_added_to)
    func = getattr(tasks, task)

    if parameters and parameters2:
        queue.enqueue(func, args=(parameters, parameters2))
    elif parameters:
        queue.enqueue(func, args=([parameters]))
    else:
        queue.enqueue(func)
    return HttpResponse(json.dumps(True), content_type='application/json')


# TASK QUEUE MANAGEMENT
@staff_member_required
def get_workers(request):

    workers = Worker.all(connection=tasks.redis_conn)

    workerdata = list()
    # serialize workers
    for w in workers:
        cj = w.get_current_job()

        if cj:
            cjinfo = {
                'id': cj.id,
                'args': cj.args,
                'enqueued_at': cj.enqueued_at.strftime(
                    "%a, %d %b %Y %H:%M:%S +0000"
                ),
                'description': cj.description}
        else:
            cjinfo = None

        worker_dict = {
            'pid': w.pid,
            'name': w.name,
            'state': w.get_state(),
            'current_job': cjinfo}

        workerdata.append(worker_dict)
    data = json.dumps(workerdata)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def delete_task_from_queue(request):
    job_id = request.GET.get('job_id')
    tasks.delete_task_from_queue(job_id)
    return HttpResponse('Success')


@staff_member_required
def delete_all_tasks_from_queue(request):
    queue_name = request.GET.get('queue_name')
    tasks.delete_all_tasks_from_queue(queue_name)
    return HttpResponse('Success')


@staff_member_required
def get_current_job(request):
    from rq import get_current_job
    from rq import Queue

    q = Queue(connection=tasks.redis_conn)
    job = get_current_job(q)
    import json
    data = json.dumps(job)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def add_scheduled_task(request):
    from rq_scheduler import Scheduler
    from datetime import datetime

    task = request.GET.get('task')
    period = request.GET.get('period')
    queue = request.GET.get('queue')
    parameters = request.GET.get('parameters')
    scheduler = Scheduler(queue_name=queue, connection=tasks.redis_conn)

    if parameters:
        scheduler.schedule(
            scheduled_time=datetime.utcnow(),   # Time for first execution
            func=getattr(tasks, task),       # Function to be queued
            args=(parameters,),
            # Time before the function is called again, in seconds
            interval=int(period),
            # Repeat this number of times (None means repeat forever)
            repeat=None
        )
    else:
        scheduler.schedule(
            scheduled_time=datetime.utcnow(),   # Time for first execution
            func=getattr(tasks, task),       # Function to be queued
            # Time before the function is called again, in seconds
            interval=int(period),
            # Repeat this number of times (None means repeat forever)
            repeat=None
        )
    return HttpResponse('Success')


@staff_member_required
def get_queue(request):

    current_queue = request.GET.get('queue')
    queue = django_rq.get_queue(current_queue)
    jobdata = list()

    count_jobs = 0
    for job in queue.jobs:
        count_jobs += 1
        if count_jobs == 6:
            break

        job_dict = {
            'job_id': job._id,
            'created_at': job.created_at.strftime(
                "%a, %d %b %Y %H:%M:%S +0000"
            ),
            'enqueued_at': job.enqueued_at.strftime(
                "%a, %d %b %Y %H:%M:%S +0000"
            ),
            'status': job.get_status(),
            'function': job.func_name,
            'args': job.args}

        jobdata.append(job_dict)
    data = json.dumps(jobdata)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def get_scheduled_tasks(request):

    # Use RQ's default Redis connection
    # use_connection()
    # Get a scheduler for the "default" queue
    scheduler = Scheduler(connection=tasks.redis_conn)
    list_of_job_instances = scheduler.get_jobs()

    jobdata = list()
    for job in list_of_job_instances:
        if "interval" in job.meta:
            interval = job.meta["interval"]
        else:
            interval = 0

        job_dict = {
            'job_id': job._id,
            'task': job.description,
            'period': interval,
            'args': job.args,
            'queue': "default"}

        jobdata.append(job_dict)

    data = json.dumps(jobdata)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def cancel_scheduled_task(request):

    from rq_scheduler import Scheduler
    job_id = request.GET.get('job_id')

    scheduler = Scheduler('default', connection=tasks.redis_conn)
    scheduler.cancel(job_id)
    return HttpResponse('Success')


@staff_member_required
def get_failed_tasks(request):

    queue = django_rq.get_failed_queue()

    jobdata = list()
    for job in queue.jobs:

        job_dict = {
            'job_id': job.id,
            'func_name': job.description,
            'error_message': job.exc_info,
            'ended_at': job.ended_at.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            'enqueued_at': job.enqueued_at.strftime(
                "%a, %d %b %Y %H:%M:%S +0000"
            ),
            'args': job.args
        }

        jobdata.append(job_dict)

    data = json.dumps(jobdata)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def get_finished_tasks(request):

    current_queue = request.GET.get('queue')
    queue = django_rq.get_queue(current_queue)
    registry = FinishedJobRegistry(queue.name, queue.connection)

    items_per_page = 10
    num_jobs = len(registry)
    jobs = []

    if num_jobs > 0:
        offset = 0
        job_ids = registry.get_job_ids(offset, items_per_page)

        for job_id in job_ids:
            try:
                jobs.append(Job.fetch(job_id, connection=queue.connection))
            except NoSuchJobError:
                pass

    jobdata = list()
    for job in jobs:

        job_dict = {
            'job_id': job.id,
            'func_name': job.func_name,
            'ended_at': job.ended_at.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            'enqueued_at': job.enqueued_at.strftime(
                "%a, %d %b %Y %H:%M:%S +0000"
            ),
            'args': job.args}

        jobdata.append(job_dict)

    data = json.dumps(jobdata)
    return HttpResponse(data, content_type='application/json')


@staff_member_required
def reschedule_all_failed(request):

    queue = get_failed_queue(get_connection())

    for job in queue.jobs:
        requeue_job(job.id, connection=queue.connection)

    return HttpResponse('Success')
