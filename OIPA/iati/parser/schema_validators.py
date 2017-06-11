import os
import os.path
from lxml import etree


def validate(iati_parser, xml_etree):
    base = os.path.dirname(os.path.abspath(__file__))
    location = base + "/../schemas/"+iati_parser.VERSION+"/iati-activities-schema.xsd"
    xsd_data = open(location)
    xmlschema_doc = etree.parse(xsd_data)
    xsd_data.close()

    xmlschema = etree.XMLSchema(xmlschema_doc)
    xml_errors = None

    try:
        xmlschema.assertValid(xml_etree)
    except etree.DocumentInvalid, xml_errors:
        pass

    if xml_errors:
        for error in xml_errors.error_log:
            iati_parser.append_error('XsdValidationError',"Todo", "Todo", error.message, error.line)
