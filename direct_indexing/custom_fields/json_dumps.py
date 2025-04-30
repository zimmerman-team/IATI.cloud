import json
import logging

JSON_FIELDS = [
    "reporting-org",
    "title",
    "description",
    "participating-org",
    "other-identifier",
    "activity-date",
    "contact-info",
    "recipient-country",
    "recipient-region",
    "location",
    "sector",
    "tag",
    "country-budget-items",
    "humanitarian-scope",
    "policy-marker",
    "default-aid-type",
    "budget",
    "planned-disbursement",
    "transaction",
    "document-link",
    "related-activity",
    "legacy-data",
    "conditions",
    "result",
    "crs-add",
    "fss",
]


def add_json_dumps(activity):
    for field in JSON_FIELDS:
        if field in activity:
            if isinstance(activity[field], list):
                _json_dump_list(activity, field)
            else:
                try:
                    activity[f'json.{field}'] = json.dumps(activity[field])
                except Exception as e:
                    logging.error(f"Error serializing {field}: type: {type(e)} stack: {e}")


def _json_dump_list(activity, field):
    activity[f'json.{field}'] = []
    for item in activity[field]:
        try:
            activity[f'json.{field}'].append(json.dumps(item))
        except Exception as e:
            logging.error(f"Error serializing {field}: type: {type(e)} stack: {e}")
