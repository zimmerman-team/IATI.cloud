from django.contrib.admin.views.decorators import staff_member_required
from task_queue import tasks
from api.v3.resources.activity_view_resources import HttpResponse


# PARSE TASKS

@staff_member_required
def add_task(request):
    import django_rq
    task = request.GET.get('task')
    parameters = request.GET.get('parameters')
    queue_to_be_added_to = request.GET.get('queue')
    queue = django_rq.get_queue(queue_to_be_added_to)

    if parameters:
        queue.enqueue(getattr(tasks, task), parameters)
    else:
        queue.enqueue(getattr(tasks, task))
    return HttpResponse('Success')




# TASK QUEUE MANAGEMENT

@staff_member_required
def start_worker(request):
    queue_name = request.GET.get('queue_name')
    tasks.start_worker(queue_name)
    return HttpResponse('Success')

@staff_member_required
def advanced_start_worker(request):
    tasks.advanced_start_worker()
    return HttpResponse('Success')


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
    job = get_current_job()
    import json
    return json.dumps(job)





# Schedule management

@staff_member_required
def add_scheduled_task(request):

    task = request.GET.get('task')
    period = request.GET.get('period')
    queue = request.GET.get('queue')


    from rq import use_connection
    from rq_scheduler import Scheduler
    from datetime import datetime

    use_connection() # Use RQ's default Redis connection
    scheduler = Scheduler(queue) # Get a scheduler for the "default" queue

    scheduler.schedule(
        scheduled_time=datetime.now(),   # Time for first execution
        func=getattr(tasks, task),           # Function to be queued
        interval=period,                 # Time before the function is called again, in seconds
        repeat=None                      # Repeat this number of times (None means repeat forever)
    )
    return HttpResponse('Success')


@staff_member_required
def get_queue(request):
    import django_rq
    import json
    current_queue = request.GET.get('queue')
    queue = django_rq.get_queue(current_queue)
    jobdata = list()

    count_jobs = 0
    for job in queue.jobs:
        count_jobs += 1
        if count_jobs == 20:
            break

        job_dict = { 'job_id': job._id, 'created_at':job.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000"), 'enqueued_at':job.enqueued_at.strftime("%a, %d %b %Y %H:%M:%S +0000"), 'status': job.status, 'function': job.func_name, 'args': job.args }
        jobdata.append(job_dict)
    data = json.dumps(jobdata)
    return HttpResponse(data, mimetype='application/json')

@staff_member_required
def get_scheduled_tasks(request):
    from rq import use_connection
    from rq_scheduler import Scheduler
    import json

    use_connection() # Use RQ's default Redis connection
    scheduler = Scheduler() # Get a scheduler for the "default" queue
    list_of_job_instances = scheduler.get_jobs()

    jobdata = list()
    for job in list_of_job_instances:
        if "interval" in job.meta:
            interval = job.meta["interval"]
        else:
            interval = 0
        job_dict = { 'job_id': job._id, 'task': job.description, 'period': interval, 'queue': "default" }
        jobdata.append(job_dict)

    # scheduler = Scheduler('parser') # Get a scheduler for the "parser" queue
    # list_of_job_instances = scheduler.get_jobs()
    #
    # for job in list_of_job_instances:
    #     if "interval" in job.meta:
    #         interval = job.meta["interval"]
    #     else:
    #         interval = 0
    #     job_dict = { 'job_id': job._id, 'task': job.description, 'period': interval, 'queue': "parser" }
    #     jobdata.append(job_dict)

    data = json.dumps(jobdata)
    return HttpResponse(data, mimetype='application/json')

@staff_member_required
def cancel_scheduled_task(request):
    job_id = request.GET.get('job_id')
    from rq import use_connection
    from rq_scheduler import Scheduler

    use_connection()
    scheduler = Scheduler('parser')
    scheduler.cancel(job_id)
    return HttpResponse('Success')






# Failed tasks

def get_failed_tasks(request):
    import django_rq
    import json
    from time import strftime

    queue = django_rq.get_failed_queue()

    jobdata = list()
    for job in queue.jobs:
        job_dict = { 'job_id' : job.id, 'func_name': job.func_name, 'error_message': job.exc_info, 'ended_at': job.ended_at.strftime("%a, %d %b %Y %H:%M:%S +0000"), 'enqueued_at' : job.enqueued_at.strftime("%a, %d %b %Y %H:%M:%S +0000")}
        jobdata.append(job_dict)

    data = json.dumps(jobdata)
    return HttpResponse(data, mimetype='application/json')






#
# @staff_member_required
# def add_task_parse_all(request):
#     tasks.parse_all_existing_sources()
#     return HttpResponse('Success')
#
# @staff_member_required
# def get_new_sources_from_iati_api(request):
#     import django_rq
#     django_rq.enqueue(tasks.get_new_sources_from_iati_api)
#     return HttpResponse('Success')
#
# @staff_member_required
# def parse_all_not_parsed_in_x_days(request):
#     import django_rq
#     days = request.GET.get('days')
#     django_rq.enqueue(tasks.parse_all_not_parsed_in_x_days, days)
#     return HttpResponse('Success')
#
# # OTHER TASKS
#
# @staff_member_required
# def update_all_geo_data(request):
#     import django_rq
#     django_rq.enqueue(tasks.update_all_geo_data)
#     return HttpResponse('Success')
#
# @staff_member_required
# def update_all_indicator_data(request):
#     import django_rq
#     django_rq.enqueue(tasks.update_all_indicator_data)
#     return HttpResponse('Success')
#
# @staff_member_required
# def cache_long_api_calls(request):
#     import django_rq
#     django_rq.enqueue(tasks.cache_long_api_calls)
#     return HttpResponse('Success')
#
# @staff_member_required
# def update_existing_api_call_caches(request):
#     import django_rq
#     django_rq.enqueue(tasks.update_existing_api_call_caches)
#     return HttpResponse('Success')






#
# # Schedule management
#
# @staff_member_required
# def add_scheduled_task(request):
#
#     task = request.GET.get('task')
#     period = request.GET.get('period')
#
#     from rq import use_connection
#     from rq_scheduler import Scheduler
#     from datetime import datetime
#
#     use_connection() # Use RQ's default Redis connection
#     scheduler = Scheduler() # Get a scheduler for the "default" queue
#
#     scheduler.schedule(
#         scheduled_time=datetime.now(),   # Time for first execution
#         func=getattr(tasks, task),           # Function to be queued
#         interval=period,                 # Time before the function is called again, in seconds
#         repeat=None                      # Repeat this number of times (None means repeat forever)
#     )
#     return HttpResponse('Success')



# @staff_member_required
# def add_task(request):
#     context = dict()
#     context['title'] = 'Add task'
#     t = TemplateResponse(request, 'admin/task_queue/add_task.html', context)
#     return t.render()

# @staff_member_required
# def scheduler(request):
#     from rq_scheduler import Scheduler
#     from rq import use_connection
#
#     context = dict()
#     context['title'] = 'Scheduler'
#     use_connection() # Use RQ's default Redis connection
#     scheduler = Scheduler()
#     context['jobs'] = scheduler.get_jobs()
#
#     t = TemplateResponse(request, 'admin/task_queue/scheduler.html', context)
#     return t.render()