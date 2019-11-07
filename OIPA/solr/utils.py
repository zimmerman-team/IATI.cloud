from django.core.exceptions import ObjectDoesNotExist


def add_value_list(data_list, value=None):
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


def date_string(value):
    if value:
        return value.strftime('%Y-%m-%dT00:00:00Z')

    return None


def decimal_string(value):
    if value:
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
        add_value_list(lang_list, narrative.language_id)
        add_value_list(narrative_list, narrative.content)

    return lang_list, narrative_list


def add_reporting_org(serializer, activity):
    reporting_organisation = activity.reporting_organisations.first()
    if reporting_organisation:
        serializer.add_field('reporting_org_ref', reporting_organisation.ref)
        serializer.add_field(
            'reporting_org_type',
            reporting_organisation.type_id
        )
        serializer.add_field(
            'reporting_org_secondary_reporter',
            bool_string(reporting_organisation.secondary_reporter)
        )
        serializer.add_field(
            'reporting_org_narrative',
            getattr(reporting_organisation.organisation, 'primary_name', None)
        )


def get_child_attr(data, field):
    attrs = field.split('.')
    value = None
    for attr in attrs:
        value = getattr(data, attr, None)
        if value:
            data = value
        else:
            break

    return value


def field_narrative(serializer, field, key):
    if field:
        for narrative in field.narratives.all():
            serializer.add_value_list(key, narrative.content)
