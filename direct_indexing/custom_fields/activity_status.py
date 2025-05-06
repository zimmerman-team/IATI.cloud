from collections import OrderedDict


def activity_status(data):
    """
    Requested by Stefanos. Single valued field.
    Retrieve the activity status code and provide it in plain text.

    :param data: reference to the activity in the data
    """
    if type(data) not in [dict, OrderedDict]:
        return data
    if 'activity-status' not in data:
        return data
    code = data['activity-status']['code']
    status_mapping = {
        1: "Pipeline/identification",
        2: "Implementation",
        3: "Finalisation",
        4: "Closed",
        5: "Cancelled",
        6: "Suspended",
    }
    data['activity-status.text'] = status_mapping.get(int(code), "Unknown")
    return data
