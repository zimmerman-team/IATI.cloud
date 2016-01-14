def get_serializer_fields(serializer):
    return serializer().get_fields().keys()

def parameter_from_type_query_param(query_param):
    """Returns type name from query_param string."""
    is_type = False
    type_name = []

    for c in query_param:
        if c == '[' and not is_type:
            is_type = True
        elif c == ']' and is_type:
            is_type = False
        elif is_type:
            type_name.append(c)

    return ''.join(type_name)


def query_params_from_context(context):
    """Returns query_params dict from context."""
    query_params = None
    try:
        query_params = context['request'].query_params
    except (KeyError, AttributeError):
        pass
    return query_params


def get_type_parameters(name, query_params):
    """
    Returns query_params dict filtered by type.
    """
    result_fields = {}
    fields_dict = {k: v for k, v in query_params.items()
                   if k.startswith(name)}

    for k, v in fields_dict.items():
        type_name = parameter_from_type_query_param(k)
        type_value = v
        result_fields[type_name] = type_value

    return result_fields
