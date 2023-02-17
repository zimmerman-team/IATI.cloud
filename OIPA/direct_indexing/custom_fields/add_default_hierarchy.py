HIER = 'hierarchy'


def add_default_hierarchy(data):
    """
    Requested by FCDO.
    "If hierarchy is not reported then 1 is assumed."

    :param data: reference to the activity in the data
    """
    if HIER not in data:
        data[HIER] = 1
    return data
