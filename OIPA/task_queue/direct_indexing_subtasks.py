import celery

from direct_indexing.processing import dataset as dataset_processing


class ProcessDatasetTask(celery.Task):
    def run(self, dataset, cl, cu, *args, **kwargs):
        result = dataset_processing.run(dataset, cl, cu)
        return result

