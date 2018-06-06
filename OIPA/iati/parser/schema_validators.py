import os
import os.path

from lxml import etree

from common.util import findnth_occurence_in_string


def validate(iati_parser, xml_etree):
    base = os.path.dirname(os.path.abspath(__file__))
    location = base + "/../schemas/" + iati_parser.VERSION \
        + "/iati-activities-schema.xsd"
    xsd_data = open(location)
    xmlschema_doc = etree.parse(xsd_data)
    xsd_data.close()

    xmlschema = etree.XMLSchema(xmlschema_doc)
    xml_errors = None

    try:
        xmlschema.assertValid(xml_etree)
    except etree.DocumentInvalid as e:
        xml_errors = e

        pass

    if xml_errors:
        for error in xml_errors.error_log:
            element = error.message[
                (findnth_occurence_in_string(
                    error.message, '\'', 0
                ) + 1):findnth_occurence_in_string(
                    error.message, '\'', 1
                )
            ]
            attribute = '-'
            if 'attribute' in error.message:
                attribute = error.message[
                    (findnth_occurence_in_string(
                        error.message, '\'', 2
                    ) + 1):findnth_occurence_in_string(
                        error.message, '\'', 3
                    )
                ]

            iati_parser.append_error(
                'XsdValidationError',
                element,
                attribute,
                error.message.split(':')[0],
                error.line,
                error.message.split(':')[1],
                'unkown for XSD validation errors')
