def index_many_to_many_relations(activity):
    # Index result indicator, starting with baseline:
    # An indicator has 0 to N baselines, if 0, represent with index -1, else represent with index n.
    if 'result' in activity:
        add_result_child_indexes(activity['result'], 'indicator')


def add_result_child_indexes(field, child):
    if type(field[child]) != list:
        field[child] = [field[child]]
    add_field_child_field_indexes(field, child, 'baseline')
    add_field_child_field_indexes(field, child, 'period')
    add_field_child_field_children_indexes(field, child, 'period', children=['actual', 'target'])


def add_field_child_field_indexes(data, target_field, field):
    total_field = 0
    data[f'{target_field}.{field}-index'] = []
    if target_field not in data:
        return
    for target in data[target_field]:
        field_index = -1
        if field in target:
            field_index = total_field
            if type(target[field]) != list:
                total_field += 1
            else:
                total_field += len(target[field])
        data[f'{target_field}.{field}-index'].append(field_index)


def add_field_child_field_children_indexes(data, target_field, field, children):
    """
    We need to have a separate function for this, it cannot be recursive, because
    we need to store this information at the base level of the budget, rather than
    in the "second level" child of data, to maintain a complete index.

    :param data: the data object
    :param target_field: the first level child of data, like an indicator
    :param field: the second level child of data, like indicator.period
    :param children: a list of third level children, such as indicator.period.actual
    """
    # Loop over the desired children
    for child in children:
        total_field = 0
        data[f'{target_field}.{field}.{child}-index'] = []
        # Only if the target field is available
        if target_field not in data:
            return
        # For every first level child we need to check for second level children.
        for target in data[target_field]:
            if field in target:
                # If the second level child is found, loop over this and check if the third level children are found.
                if type(target[field]) != list:
                    target[field] = [target[field]]
                # target[field] is now a list of the second level children
                # for every second level child, check if the third level children are found
                # Use enumerate to only save the index of for the first occurrence.
                for i, item in enumerate(target[field]):
                    if child in item:
                        field_index = total_field
                        if type(item[child]) != list:
                            total_field += 1
                        else:
                            total_field += len(item[child])
                    else:
                        field_index = -1
                    data[f'{target_field}.{field}.{child}-index'].append(field_index)
