from django.conf.urls import url

from task_queue.views import (
    add_scheduled_task, add_task, cancel_scheduled_task,
    delete_all_tasks_from_queue, delete_task_from_queue, get_current_job,
    get_failed_tasks, get_finished_tasks, get_queue, get_scheduled_tasks,
    get_workers, reschedule_all_failed
)

urlpatterns = [
    # Task queue management
    url(r'^get_workers/', get_workers),
    url(r'^delete_task_from_queue/', delete_task_from_queue),
    url(r'^delete_all_tasks_from_queue/', delete_all_tasks_from_queue),
    url(r'^get_current_job/', get_current_job),
    url(r'^get_queue/', get_queue),
    # Callable tasks
    url(r'^add_task/', add_task),
    # Schedule management
    url(r'^add_scheduled_task/', add_scheduled_task),
    url(r'^cancel_scheduled_task/', cancel_scheduled_task),
    url(r'^get_scheduled_tasks/', get_scheduled_tasks),
    # Failed task management
    url(r'^get_failed_tasks/', get_failed_tasks),
    url(r'^reschedule_all_failed/', reschedule_all_failed),
    # Finished tasks
    url(r'^get_finished_tasks/', get_finished_tasks)
]
