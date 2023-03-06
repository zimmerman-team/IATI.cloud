def dataset_metadata(metadata):
    """
    Select a subset of the dataset metadata to be stored alongside each
    activity or organisation entry. The subset is defined in the
    `fields` and `multivalued_fields` lists.
    """
    fields = [
        "id",
        "metadata_created",
        "metadata_modified",
        "name",
        "extras.iati_version",
        "extras.publisher_iati_id",
        "extras.publisher",
        "extras.validation_status"
    ]
    multivalued_fields = [
        "hash",
        "last_modified",
        "url",
    ]
    custom_metadata = {}

    for field in fields:
        if field in metadata:
            custom_metadata[f'dataset.{field}'] = metadata[field]
    for field in multivalued_fields:
        if 'resources' not in metadata:
            continue
        if field in metadata['resources'][0]:
            custom_metadata[f'dataset.resources.{field}'] = metadata['resources'][0][field]
    return custom_metadata


def add_meta_to_activity(activity, metadata):
    """
    Add the dataset metadata to the activity.
    """
    for field in metadata:
        activity[field] = metadata[field]
    return activity
