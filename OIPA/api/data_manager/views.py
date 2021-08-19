from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from iati_synchroniser.models import Dataset, Publisher
from OIPA import settings
from task_queue.tasks import (
    priority_queue_parse_source, priority_queue_sync_dataset
)


# Helper functions
def handle_dataset_update(registry_updated, dataset, auth):
    """
    1. Check auth.
    2. if Registry_updated, use custom dataset synchronization for the
        specified dataset, to synchronize new or changed data,
        like the source_url.
    3. Ensure the dataset with iati_id is marked as “Managed by AIDA”
    4. Run the priority_source_by_id task in the AIDA priority queue.
    """
    if auth != settings.AIDA_IATICLOUD_AUTH:
        return "Not authorized."

    if registry_updated != "no":
        priority_queue_sync_dataset.delay(dataset_id=dataset)
        return "Dataset has been added to Synchronisation and will be added" \
               " to the Priority Parsing Queue."
    else:
        d = Dataset.objects.filter(iati_id=dataset).first()
        if not d:
            return "Dataset could not be found."
        if not d.managed_by_aida:
            d.managed_by_aida = True
            d.save()
        priority_queue_parse_source.delay(dataset_id=d.id,
                                          force=False,
                                          check_validation=False)
        return "Dataset has been added to the Priority Parsing Queue."


def handle_registration_update(publisher, register, auth):
    """
    Function Largely explained by return values.
    Update datasets to reflect the requested registration status change
    """
    if auth != settings.AIDA_IATICLOUD_AUTH:
        return "Not authorized."
    if register != "register" and register != "unregister":
        return "Registration value not recognized."
    managed_by_aida = register == "register"

    # Get publisher id from publisher IATI id.
    p_id = Publisher.objects.filter(iati_id=publisher).first().id
    if not p_id:
        return "No publisher with that ID found."

    # Get all datasets belonging to the publisher
    datasets = Dataset.objects.filter(publisher_id=p_id)
    if datasets:
        for d in datasets:
            d.managed_by_aida = managed_by_aida
            d.save()

    if managed_by_aida:
        return "Datasets for publisher now managed by AIDA."
    else:
        return "Datasets for publisher no longer managed by AIDA."


# Actual calls available in the urls.py
@csrf_exempt
def dataset_update(request):
    """
    POST request
    Body requirements:
        registry_updated:       string, yes or no
        dataset_iati_id:        string, the IATI Identifier belonging to the
            managed dataset, marked as ID in the iati registry.
        AIDA_IATICLOUD_AUTH:    An environment variable to ensure this endpoint
            is accessed by AIDA.
    """
    if request.method != "POST":
        return HttpResponse("This endpoint can only be used to POST files.")
    try:
        response = handle_dataset_update(
            request.POST['registry_updated'],
            request.POST['dataset_iati_id'],
            request.POST['AIDA_IATICLOUD_AUTH']
        )
        return HttpResponse(response)
    except MultiValueDictKeyError:
        return HttpResponse("This POST requires 'dataset_iati_id', "
                            "'registry_updated' and the correct authentication"
                            " key.")


@csrf_exempt
def auth_registration(request):
    """
    POST request
    Body requirement:
        publisher_iati_id: string, publisher id as seen in IATI Registry
        register: string, either "register" or "unregister"
        AIDA_IATICLOUD_AUTH: string, authorisation match
    """
    if request.method != "POST":
        return HttpResponse("This endpoint can only be used to POST data.")
    try:
        response = handle_registration_update(
            request.POST['publisher_iati_id'],
            request.POST['register'],
            request.POST['AIDA_IATICLOUD_AUTH']
        )
        return HttpResponse(response)
    except MultiValueDictKeyError:
        return HttpResponse("This POST requires 'publisher_iati_id', "
                            "and the correct authentication key.")
