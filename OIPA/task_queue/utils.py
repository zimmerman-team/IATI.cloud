import time

import requests
import urllib
from celery.task.control import inspect

from iati_synchroniser.models import AsyncTasksFinished, Dataset, DatasetDownloadsStarted, InterruptIncrementalParse
from task_queue.validation import DatasetValidationTask


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


def check_incremental_parse_interrupt():
    iip = InterruptIncrementalParse.objects.all()
    ret = len(iip) > 0
    iip.delete()
    return ret


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
    check_grace_iteration_count = 0
    check_grace_iteration_maximum = 10
    check_grace_maximum_disparity = 10
    while True:
        # Get the size of the started datasets
        if not started_not_set:
            started = len(DatasetDownloadsStarted.objects.all())
        finished = len(AsyncTasksFinished.objects.all())

        # Check if the grace should take effect.
        # Grace is when the number of failed tasks is very small but the
        # number of finished tasks no longer changes. This makes sure that
        # the automatic parsing does not get stuck waiting for an unfinished
        # async task.
        if finished == check_previous_finished_length:
            check_grace_iteration_count += 1
            if check_grace_iteration_count == check_grace_iteration_maximum:
                if started - finished < check_grace_maximum_disparity:
                    break
                else:  # More async tasks than expected failed,
                    # exit automatic parsing
                    return True
        else:
            check_grace_iteration_count = 0

        # Check if the async tasks are done
        if started == finished:
            if finished == check_previous_finished_length:
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


def automatic_incremental_validation(start_at, check_validation):
    # STEP THREE -- DATASET VALIDATION TASK #
    # Only execute this step if validation should be active.
    if start_at in (1, 2, 3) and check_validation:
        # Prepare checks
        check_validation_has_started = False
        check_validation_is_active = False
        check_empty_iteration_count = 0
        check_empty_iteration_maximum = 3

        while True:
            url = "https://iativalidator.iatistandard.org/api/v1/queue/next"
            response = requests.get(url, timeout=30)

            # If the response is not 200, reset and check back later.
            if response.status_code != 200:
                check_validation_has_started = False
                check_validation_is_active = False
                time.sleep(60)
                continue

            check_content_is_empty = response.content.decode("utf-8") == ""

            """
            Case 1: content empty - started = false - active = false
                wait for the validator to start
            Case 2: content has data - started = false - active = false
                set started to true and active to true
            Case 3: content has data - started = true - active = true
                wait for the content to stop having data!
            Case 4: content empty - started = true - active = true
                with three iterations, confirm the content is actually empty!
                set active to false.
            """
            # if check_content_is_empty and not check_validation_has_started and not check_validation_is_active:  # NOQA: E501
            if not check_content_is_empty and not check_validation_has_started and not check_validation_is_active:  # NOQA: E501
                check_validation_has_started = True
                check_validation_is_active = True
            if not check_content_is_empty and check_validation_has_started and check_validation_is_active:  # NOQA: E501
                check_empty_iteration_count = 0
            if check_content_is_empty and check_validation_has_started and check_validation_is_active:  # NOQA: E501
                if check_empty_iteration_count < check_empty_iteration_maximum:
                    check_empty_iteration_count += 1
                else:  # Validation has finished
                    break
            time.sleep(60)

        # Now that the "waiting for validator to finish" loop is over, we know
        # The validator is finished. Run the task. To reduce complexity, reuse
        # the AsyncTasksFinished table.
        datasets = Dataset.objects.all()
        for dataset in datasets:
            DatasetValidationTask.delay(dataset_id=dataset.id)

        started = len(Dataset.objects.all())
        await_async_subtasks(started)
    # STEP THREE -- End #


def datadump_success():
    """
    Check if the most recent IATI Data dump by CodeForIATI was a success.
    Returns true or false based on the above.
    """
    svg_url = 'https://github.com/codeforIATI/iati-data-dump/actions/workflows/refresh_data.yml/badge.svg'
    file = urllib.request.urlopen(svg_url)
    data = file.read()
    file.close()
    # data is a bytestring containing the svg, passing is not in the svg if the action failed
    return b"passing" in data
