import numbers

from django.core.exceptions import ObjectDoesNotExist
from lxml import etree


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


def date_time_string(value):
    if value:
        return value.strftime('%Y-%m-%dT%H:%M:%SZ')

    return None


def date_string(value):
    if hasattr(value, "strftime"):
        if hasattr(value, "hour"):
            offset = value.utcoffset()
            if offset:
                value = value - offset

            value = value.replace(tzinfo=None).isoformat() + "Z"
        else:
            value = "%sT00:00:00Z" % value.isoformat()

        return value

    return None


def date_quarter(value):
    if hasattr(value, "strftime") and hasattr(value, "month"):
        return ((value.month - 1) // 3) + 1
    return None


def decimal_string(value):
    if isinstance(value, numbers.Number):
        return str(value)
    else:
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
        if narrative.language_id:
            add_value_list(lang_list, narrative.language_id)
        else:
            lang_list.append(' ')
        if narrative.content:
            add_value_list(narrative_list, narrative.content)
        else:
            narrative_list.append(' ')

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
            'reporting_org_type_name',
            get_child_attr(reporting_organisation, 'type.name')
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


def make_normalized_usd_namespace_element(rate, imf_url, value, name):
    element_name = 'usd_' + name
    root = etree.Element('root')
    ns_map = {"imf": "https://www.imf.org/external/index.htm"}
    element = etree.SubElement(root,
                               "{https://www.imf.org/external/index.htm}" +
                               element_name,
                               currency='USD', exchange_rate=rate,
                               nsmap=ns_map)
    value_sub_element = etree.SubElement(element,
                                         "{https://www.imf.org/external/index.htm}" + 'usd-value', nsmap=ns_map)  # NOQA: E501
    value_sub_element.text = value
    imf_sub_element = etree.SubElement(element,
                                       "{https://www.imf.org/external/index.htm}"  # NOQA: E501
                                       + 'url', nsmap=ns_map)
    imf_sub_element.text = imf_url
    return etree.tostring(element, pretty_print=True)
