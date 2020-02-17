from celery.task.control import inspect


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
