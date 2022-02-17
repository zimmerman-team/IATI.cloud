def title_narrative_first(data):
    """
    Requested by FCDO. Single valued field.
    Retrieve the first narrative from the multivalued field.

    :param data: reference to the activity in the data
    """
    try:
        data['title.narrative.first'] = data['title']['narrative'][0]
    except:  # NOQA
        pass  # No narrative to be added
    return data
