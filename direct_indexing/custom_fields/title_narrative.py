from collections import OrderedDict


def title_narrative_first(data):
    """
    Requested by FCDO. Single valued field.
    Retrieve the first narrative from the multivalued field.

    :param data: reference to the activity in the data
    """
    if not isinstance(data, (dict, OrderedDict)):
        return data
    title = data.get('title')
    if not isinstance(title, dict):
        return data
    if 'narrative' in data['title']:
        if type(data['title']['narrative']) is list:
            data['title.narrative.first'] = data['title']['narrative'][0]
        else:
            data['title.narrative.first'] = data['title']['narrative']
    return data
