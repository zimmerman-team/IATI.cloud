def clean_dataset_metadata(dataset):
    """
    The dataset metadata contains some fields that need to be processed
    before we can index them directly into Solr. First, we want to make
    sure that if there is a list of keys, we remove any that do not have
    a value.

    In the specific case of 'extras', we also add a new field for every key,
    because this makes the data more searchable and link the key and value
    of this datapoint together.

    :param dataset: The dataset to clean.
    :return: The dataset with the cleaned metadata
    """
    # Clean resource fields by removing empty items
    if 'resources' in dataset.keys():
        clean_resources(dataset)
    if 'extras' in dataset.keys():
        clean_extras(dataset)
    return dataset


def clean_resources(dataset):
    for item in dataset['resources']:
        for key in list(item):  # use list(item) to iterate over a copy of the keys
            if item[key] == '':
                item.pop(key)


def clean_extras(dataset):
    items_to_pop = []
    for item in dataset['extras']:
        # Clean empty extra fields
        if item['value'] == '':
            items_to_pop.append(item)
        # Add single valued field names for each "extra" key.
        extras_name = f"extras.{item['key']}"
        dataset[extras_name] = item['value']
    dataset['extras'] = [d for d in dataset['extras'] if d not in items_to_pop]
