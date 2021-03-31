import time

from celery.task.control import inspect

from iati_synchroniser.models import (
    AsyncTasksFinished, DatasetDownloadsStarted
)


class Tasks:
    """
    The logic: if only one task is running then the task will
    be continued to run.
    - parent_task: if only this task is running then continued to run
    - children_task: if the active task has one or more children_task
      then not continue to run the task.
    """

    def __init__(self, parent_task, children_tasks):
        self.inspect = inspect()

        self.parent_task = parent_task
        self.children_tasks = children_tasks

    def workers(self):
        return self.inspect.active()

    def list(self):
        task_list = [self.parent_task]
        task_list.extend(self.children_tasks)

        return task_list

    def count(self):
        count = 0
        try:
            for worker in self.workers():
                for task in self.workers()[worker]:
                    if task['type'] in self.list():
                        count += 1

        except TypeError:
            pass

        return count

    def active(self):
        tasks = list()
        try:
            for worker in self.workers():
                for task in self.workers()[worker]:
                    if task['type'] in self.list() \
                            and task['type'] not in tasks:
                        tasks.append(task['type'])

        except TypeError:
            pass

        return tasks

    def is_parent(self):
        if self.count() == 1 and self.active() == [self.parent_task]:
            return True

        return False


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def reset_automatic_incremental_parse_dbs():
    dds = DatasetDownloadsStarted.objects.all()
    dds.delete()
    ddf = AsyncTasksFinished.objects.all()
    ddf.delete()


# Await asynchronous subtasks from other tasks. Started is the number of
# elements that are expected to be in
def await_async_subtasks(started=-1, started_not_set=True):
    check_iteration_count = 0
    check_iteration_maximum = 3
    check_previous_finished_length = 0
    if not started_not_set:
        check_grace_iteration_count = 0
        check_grace_iteration_maximum = 10
        check_grace_maximum_disparity = 10
    while True:
        # Get the size of the started datasets
        if not started_not_set:
            started = len(DatasetDownloadsStarted.objects.all())
        finished = len(AsyncTasksFinished.objects.all())

        if not started_not_set:
            # Check if the grace should take effect.
            if finished == check_previous_finished_length:
                check_grace_iteration_count += 1
                if check_grace_iteration_count == check_grace_iteration_maximum:  # NOQA: E501
                    if started - finished < check_grace_maximum_disparity:
                        break
                    else:  # More downloads than expected failed,
                        # exit automatic parsing
                        return True
            else:
                check_grace_iteration_count = 0

        if started == finished & finished == check_previous_finished_length:  # NOQA: E501
            check_iteration_count += 1
            if check_iteration_count == check_iteration_maximum:
                break
        else:
            check_iteration_count = 0

        # Wait a minute and check again
        time.sleep(60)
        check_previous_finished_length = finished
    # After this while loop finishes, we clear the DatasetDownloads tables
    reset_automatic_incremental_parse_dbs()
