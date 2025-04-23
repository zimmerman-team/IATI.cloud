import datetime
import json

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
    try:
        token = data["token"]
        if token != settings.SECRET_KEY:
            return JsonResponse({"error": "Invalid token"}, status=403)
    except KeyError:
        return JsonResponse({"error": "Missing required token"}, status=400)
    try:
        publisher = data["publisher"]
        ds_name = data["name"]
        ds_url = data["url"]
        ds = data["dataset"]
        # testing if organization is present in ds
        if not ds.get("organization"):
            return JsonResponse({"error": "Organization is missing in dataset"}, status=400)
        if not ds.get("resources"):
            return JsonResponse({"error": "Resources are missing in dataset"}, status=400)
        if not ds.get("extras"):
            return JsonResponse({"error": "Extras are missing in dataset"}, status=400)
        dataset = _make_dataset(ds, publisher, ds_name, ds_url)
    except KeyError:
        return JsonResponse({"error": "Missing required token"}, status=400)

    # Add a celery task to index the provided dataset.
    if direct == "no":
        aida_async_index.delay(dataset, publisher, ds_name, ds_url)
        return JsonResponse({"status": "Indexing started"}, status=202)
    else:
        status, code = aida_direct_index(dataset, publisher, ds_name, ds_url)
        return JsonResponse({"status": status}, status=code)


@csrf_exempt
def aida_drop(request):
    """
    Endpoint to drop a specific AIDA dataset.

    Expects a JSON body with the following fields:
    - direct: "yes" or "no" ("no" if not provided) used to determine if processed immediately, or as a celery task
    - token (required): The secret token to authenticate the request
    - name: The name of the dataset
    return: a JSON response with the status of the dropping process
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request, must be POST"}, status=400)

    # Get the data from the request body
    data = json.loads(request.body)
    direct = data.get("direct", "no")
    try:
        token = data["token"]
        if token != settings.SECRET_KEY:
            return JsonResponse({"error": "Invalid token"}, status=403)

        ds_name = data["name"]
    except KeyError:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # Add a celery task to index the provided dataset.
    if direct == "no":
        aida_async_drop.delay(ds_name)
        return JsonResponse({"status": "Indexing started"}, status=202)
    else:
        status, code = aida_direct_drop(ds_name)
        return JsonResponse({"status": status}, status=code)


def _make_dataset(dataset, publisher, ds_name, ds_url):
    """
    Used this dataset to define the base requirements:
    https://iatiregistry.org/api/3/action/package_show?id=fcdo-set-1

    Reconstruct a complete iati registry dataset object from the provided dataset,
    in case of any missing fields.
    """
    try:
        dso = dataset.get("organization")
        dse = dataset.get("extras")
        dsr = dataset.get("resources")[0]

        return {
            "author": dataset.get("author", None),
            "author_email": dataset.get("author_email", ""),
            "creator_user_id": dataset.get("creator_user_id", ""),
            "id": dataset.get("id", ""),
            "isopen": dataset.get("isopen", True),
            "license_id": dataset.get("license_id", "MIT"),
            "license_title": dataset.get("license_title", "MIT License"),
            "license_url": dataset.get("license_url", None),
            "maintainer": dataset.get("maintainer", None),
            "maintainer_email": dataset.get("maintainer_email", None),
            "metadata_created": dataset.get("metadata_created", datetime.datetime.now()),
            "metadata_modified": dataset.get("metadata_modified", datetime.datetime.now()),
            "name": ds_name,
            "notes": dataset.get("notes", ""),
            "num_resources": dataset.get("num_resources", 1),
            "num_tags": dataset.get("num_tags", 0),
            "organization": {
                "id": dso.get("id", None),
                "name": publisher,
                "title": dso.get("title", publisher),
                "type": dso.get("type", "organization"),
                "description": dso.get("description", ""),
                "image_url": dso.get("image_url", None),
                "created": dso.get("created", datetime.datetime.now()),
                "is_organization": dso.get("is_organization", True),
                "approval_status": dso.get("approval_status", "approved"),
                "state": dso.get("active", "active"),
            },
            "owner_org": dataset.get("owner_org", None),
            "private": dataset.get("private", False),
            "state": dataset.get("state", "active"),
            "title": dataset.get("title", ds_name),
            "type": dataset.get("type", "dataset"),
            "url": dataset.get("url", None),
            "version": dataset.get("version", None),
            "extras": [
                {
                    "key": dse[0].get("key", "activity_count"),
                    "value": dse[0].get("value", "0")
                },
                {
                    "key": dse[1].get("key", "country"),
                    "value": dse[1].get("value", "")
                },
                {
                    "key": dse[2].get("key", "data_updated"),
                    "value": dse[2].get("value", datetime.datetime.now())
                },
                {
                    "key": dse[3].get("key", "filetype"),
                    "value": dse[3].get("value", "activity")
                },
                {
                    "key": dse[4].get("key", "iati_version"),
                    "value": dse[4].get("value", "2.03")
                },
                {
                    "key": dse[5].get("key", "language"),
                    "value": dse[5].get("value", "")
                },
                {
                    "key": dse[6].get("key", "secondary_publisher"),
                    "value": dse[6].get("value", "")
                },
                {
                    "key": dse[7].get("key", "validation_status"),
                    "value": dse[7].get("value", "Unknown")
                }
            ],
            "resources": [
                {
                    "cache_last_updated": dsr.get("cache_last_updated", None),
                    "cache_url": dsr.get("cache_url", None),
                    "created": dsr.get("created", datetime.datetime.now()),
                    "description": dsr.get("description", ""),
                    "format": dsr.get("format", "IATI-XML"),
                    "hash": dsr.get("hash", "updateme"),
                    "id": dsr.get("id", None),
                    "last_modified": dsr.get("last_modified", None),
                    "metadata_modified": dsr.get("metadata_modified", datetime.datetime.now()),
                    "mimetype": dsr.get("mimetype", ""),
                    "mimetype_inner": dsr.get("mimetype_inner", None),
                    "name": dsr.get("name", ds_name),
                    "package_id": dsr.get("package_id", ""),
                    "position": dsr.get("position", 0),
                    "resource_type": dsr.get("resource_type", None),
                    "size": dsr.get("size", 0),
                    "state": dsr.get("state", "active"),
                    "url": ds_url,
                    "url_type": dsr.get("url_type", None)
                }
            ],
            "tags": dataset.get("tags", []),
            "groups": dataset.get("groups", []),
            "relationships_as_subject": dataset.get("relationships_as_subject", []),
            "relationships_as_object": dataset.get("relationships_as_object", [])
        }
    except KeyError as e:
        raise e
