from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


def add_list(data_list=list, value=None):
    if value:
        data_list.append(value)


def add_dict(data_dict=dict, field=None, value=None):
    if value and field and isinstance(field, str):
        data_dict[field] = value


def bool_string(value=bool):
    return '1' if value else '0'


def value_string(value):
    if value:
        return str(value)

    return None


def decimal_string(value):
    if value and value > 0:
        return str(value)

    return None


def none_or_value(value):
    try:
        return value
    except ObjectDoesNotExist:
        return None


def get_narrative_lang_list(data):
    lang_list = list()
    narrative_list = list()
    for narrative in data.narratives.all():
        add_list(lang_list, narrative.language_id)
        add_list(narrative_list, narrative.content)

    return lang_list, narrative_list
