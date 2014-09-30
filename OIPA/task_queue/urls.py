# Django specific
from django.conf.urls import *
# from django_rq import urls, views

urlpatterns = patterns('',

    # Task queue management
    (r'^start_worker_with_supervisor/', 'task_queue.views.start_worker_with_supervisor'),
    (r'^get_workers/', 'task_queue.views.get_workers'),
    (r'^delete_task_from_queue/', 'task_queue.views.delete_task_from_queue'),
    (r'^delete_all_tasks_from_queue/', 'task_queue.views.delete_all_tasks_from_queue'),
    (r'^get_current_job/', 'task_queue.views.get_current_job'),
    (r'^get_queue/', 'task_queue.views.get_queue'),

    (r'^test/', 'task_queue.views.test'),

    # Callable tasks
    (r'^add_task/', 'task_queue.views.add_task'),

    # Schedule management
    (r'^start_scheduler/', 'task_queue.views.start_scheduler'),
    (r'^add_scheduled_task/', 'task_queue.views.add_scheduled_task'),
    (r'^cancel_scheduled_task/', 'task_queue.views.cancel_scheduled_task'),
    (r'^get_scheduled_tasks/', 'task_queue.views.get_scheduled_tasks'),

    #Failed task management
    (r'^get_failed_tasks/', 'task_queue.views.get_failed_tasks'),
    (r'^reschedule_all_failed/', 'task_queue.views.reschedule_all_failed'),

    # task queue pages
    # (r'', include('django_rq.urls')),

    # url(r'^$', 'django_rq.views.stats', name='rq_home'),
    # url(r'^queues/(?P<queue_index>[\d]+)/$', 'django_rq.views.jobs', name='rq_jobs'),
    # url(r'^queues/(?P<queue_index>[\d]+)/empty/$', 'django_rq.views.clear_queue', name='rq_clear'),
    # url(r'^queues/(?P<queue_index>[\d]+)/(?P<job_id>[-\w]+)/$', 'django_rq.views.job_detail', name='rq_job_detail'),
    # url(r'^queues/(?P<queue_index>[\d]+)/(?P<job_id>[-\w]+)/delete/$', 'django_rq.views.delete_job', name='rq_delete_job'),
    # url(r'^queues/actions/(?P<queue_index>[\d]+)/$', 'django_rq.views.actions', name='rq_actions'),
    # url(r'^queues/(?P<queue_index>[\d]+)/(?P<job_id>[-\w]+)/requeue/$', 'django_rq.views.requeue_job_view', name='rq_requeue_job'),


)


