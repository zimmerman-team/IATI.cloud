import datetime
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from direct_indexing.direct_indexing import aida_drop as aida_direct_drop
from direct_indexing.direct_indexing import aida_index as aida_direct_index
from direct_indexing.tasks import aida_async_drop, aida_async_index


@csrf_exempt
def aida_index(request):
    """
    Endpoint to index a specific AIDA dataset.

    Expects a JSON body with the following fields:
    - direct: "yes" or "no" ("no" if not provided) used to determine if processed immediately, or as a celery task
    - token (required): The secret token to authenticate the request, as set in IATI.cloud
    - draft (optional): Boolean to indicate if the dataset is a draft
    - publisher: The publisher name
    - name: The name of the dataset
    - url: The URL to the dataset
    return: a JSON response with the status of the indexing process
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request, must be POST"}, status=400)

    if request.content_type != "application/json":
        return JsonResponse({"error": "Invalid content type, must be application/json"}, status=400)
    # Get the data from the request body
    data = json.loads(request.body)
    direct = data.get("direct", "no")
    draft = data.get("draft", False)

    publisher = data.get("publisher", None)
    ds_name = data.get("name", None)
    ds_url = data.get("url", None)
    ds_id = data.get("id", None)

    if not publisher or not ds_name or not ds_url:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # No dataset ID provided, we generate one instead.
    if not ds_id:
        ds_id = f"{publisher}-{ds_name}"

    try:
        token = data["token"]
        if token != settings.SECRET_KEY:
            return JsonResponse({"error": "Invalid token"}, status=403)
    except KeyError:
        return JsonResponse({"error": "Missing required token"}, status=400)

    dataset = _make_dataset(ds_id, publisher, ds_name, ds_url)

    # Add a celery task to index the provided dataset.
    if direct == "no":
        aida_async_index.delay(dataset, publisher, ds_name, ds_url, draft)
        return JsonResponse({"status": "Indexing started"}, status=202)
    else:
        status, code = aida_direct_index(dataset, publisher, ds_name, ds_url, draft)
        return JsonResponse({"status": status}, status=code)


@csrf_exempt
def aida_drop(request):
    """
    Endpoint to drop a specific AIDA dataset.

    Expects a JSON body with the following fields:
    - direct: "yes" or "no" ("no" if not provided) used to determine if processed immediately, or as a celery task
    - token (required): The secret token to authenticate the request
    - draft (optional): Boolean to indicate if the dataset is a draft
    - name: The name of the dataset
    return: a JSON response with the status of the dropping process
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request, must be POST"}, status=400)

    # Get the data from the request body
    data = json.loads(request.body)
    direct = data.get("direct", "no")
    draft = data.get("draft", False)

    token = data.get("token", "")
    if token != settings.SECRET_KEY:
        return JsonResponse({"error": "Invalid token"}, status=403)

    ds_id = data.get("id", "")
    if not ds_id:
        ds_name = data.get("name", "")
        publisher = data.get("publisher", "")
        ds_id = f"{publisher}-{ds_name}"
    if ds_id == "-" or ds_id == "":
        return JsonResponse({"error": "Missing required `id` or `name` and `publisher`"}, status=400)
    # Add a celery task to index the provided dataset.
    if direct == "no":
        aida_async_drop.delay(ds_id, draft)
        return JsonResponse({"status": "Indexing started"}, status=202)
    else:
        status, code = aida_direct_drop(ds_id, draft)
        return JsonResponse({"status": status}, status=code)


def _make_dataset_organization(publisher):
    """
    Process the organization from a dataset, applying default values for missing fields.

    Args:
        publisher: The publisher name

    Returns:
        Organization with default values applied for missing fields
    """
    return {
        "id": publisher,
        "name": publisher,
        "title": publisher,
        "type": "organization",
        "description": "",
        "image_url": None,
        "created": datetime.datetime.now(),
        "is_organization": True,
        "approval_status": "approved",
        "state": "active"
    }


def _make_dataset_extras():
    """
    Process the extras list from a dataset, applying default values for missing fields.

    Returns:
        List of extras with default values applied for missing fields
    """
    # Define default extras
    default_extras = {
        "data_updated": datetime.datetime.now(),
        "filetype": "activity",
        "iati_version": "2.03",
        "validation_status": "Success"
    }

    # Convert back to list format
    return [{"key": k, "value": v} for k, v in default_extras.items()]


def _make_dataset_resources(ds_name, ds_url):
    """
    Process the resources list from a dataset, applying default values for missing fields.

    Args:
        ds_name: The name of the dataset
        ds_url: The URL to the dataset

    Returns:
        List of resources with default values applied for missing fields
    """
    return [
        {
            "cache_last_updated": None,
            "cache_url": None,
            "created": datetime.datetime.now(),
            "description": "",
            "format": "IATI-XML",
            "hash": "AIDATMPHASH",
            "id": None,
            "last_modified": None,
            "metadata_modified": datetime.datetime.now(),
            "mimetype": "",
            "mimetype_inner": None,
            "name": ds_name,
            "package_id": "",
            "position": 0,
            "resource_type": None,
            "size": 0,
            "state": "active",
            "url": ds_url,
            "url_type": None
        }
    ]


def _make_dataset(ds_id, publisher, ds_name, ds_url):
    """
    Used this dataset to define the base requirements:
    https://iatiregistry.org/api/3/action/package_show?id=fcdo-set-1

    Reconstruct a complete iati registry dataset object from the provided dataset,
    in case of any missing fields.

    Args:
        dataset: The dataset to process
        publisher: The publisher name
        ds_name: The name of the dataset
        ds_url: The URL to the dataset

    Returns:
        A complete iati registry dataset object with default values applied for missing fields
    """
    try:
        dso = _make_dataset_organization(publisher)
        dse = _make_dataset_extras()
        dsr = _make_dataset_resources(ds_name, ds_url)

        return {
            "author": None,
            "author_email": None,
            "creator_user_id": None,
            "id": ds_id,
            "isopen": True,
            "license_id": "MIT",
            "license_title": "MIT License",
            "license_url": None,
            "maintainer": None,
            "maintainer_email": None,
            "metadata_created": datetime.datetime.now(),
            "metadata_modified": datetime.datetime.now(),
            "name": ds_name,
            "notes": "",
            "num_resources": 1,
            "num_tags": 0,
            "organization": dso,
            "owner_org": None,
            "private": False,
            "state": "active",
            "title": ds_name,
            "type": "dataset",
            "url": None,
            "version": None,
            "extras": dse,
            "resources": dsr,
            "tags": [],
            "groups": [],
            "relationships_as_subject": [],
            "relationships_as_object": [],
            "iati_cloud_aida_sourced": True
        }
    except KeyError as e:
        logging.error(f"KeyError in _make_dataset: {e}")
        raise e
