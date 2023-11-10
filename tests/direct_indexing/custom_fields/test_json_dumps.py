import json

from direct_indexing.custom_fields.json_dumps import add_json_dumps


def test_add_json_dumps():
    # Test nothing changes if activity is empty
    activity = {}
    add_json_dumps(activity)
    assert activity == {}

    # Test if an activity is present, but the field is not in JSON fields, nothing changes to the activity
    activity = {"test": 1}
    add_json_dumps(activity)
    assert activity == {"test": 1}

    # Test if an activity is present, the field is in JSON_FIELDS, the field is a dict,
    # the data is added as a single json string
    activity = {"title": {"narrative": "test"}}
    expected_res = activity.copy()
    expected_res['json.title'] = json.dumps(activity['title'])
    add_json_dumps(activity)
    assert activity == expected_res

    # Test if an activity is present, the field is in JSON_FIELDS, the field is a list,
    # the data is added as a list of json strings
    activity = {"title": [{"narrative": "test"}, {"narrative": "toast"}]}
    expected_res = activity.copy()
    expected_res['json.title'] = [json.dumps(activity['title'][0]), json.dumps(activity['title'][1])]
    add_json_dumps(activity)
    assert activity == expected_res
