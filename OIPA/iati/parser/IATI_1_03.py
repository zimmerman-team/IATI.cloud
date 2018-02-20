from IATI_1_05 import Parse as IATI_105_Parser
from iati import models
from geodata.models import Country, Region
import dateutil.parser
from lxml.builder import E
from iati_codelists import models as codelist_models
from iati.parser.exceptions import *


class Parse(IATI_105_Parser):

    # maps to geographic vocabulary
    gazetteer_agency_mapping = {
        "GEO": "G1",
        "OSM": "G2",
    }

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '1.03'

    '''atributes:
    code:ADM2
    {http://www.w3.org/XML/1998/namespace}lang:en

    tag:location-type'''

    def iati_activities__iati_activity__location__administrative(self, element):
        country = element.attrib.get('country')
        adm1 = element.attrib.get('adm1')
        adm2 = element.attrib.get('adm2')

        if country:
            # ISO Country (3166-1 alpha-2)
            elem = E('administrative', code=country, vocabulary="A4")
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        if adm1:
            # UN Second Administrative Level Boundary Project
            elem = E('administrative', code=country, vocabulary="A2", level="1")
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        if adm2:
            # UN Second Administrative Level Boundary Project
            elem = E('administrative', code=country, vocabulary="A2", level="2")
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        return element

    '''atributes:
    latitude:36.79256
    longitude:68.84385
    precision:3

    tag:coordinates'''

    def iati_activities__iati_activity__location__coordinates(self, element):
        latitude = element.attrib.get('latitude')
        longitude = element.attrib.get('longitude')
        precision = element.attrib.get('precision')

        if not latitude:
            raise RequiredFieldError(
                "location/coordinates",
                "latitude",
                "required attribute missing")

        if not longitude:
            raise RequiredFieldError(
                "location/coordinates",
                "longitude",
                "required attribute missing")

        point = E('point')
        super(Parse, self).iati_activities__iati_activity__location__point(point)
        pos = E('pos', latitude + ' ' + longitude)  # ISO Country (3166-1 alpha-2)
        super(Parse, self).iati_activities__iati_activity__location__point__pos(pos)

        if precision:
            if precision != "1":
                precision = "2"  # Everything but "Exact" is "Approximate"
            exactness = E('exactness', code=precision)
            super(Parse, self).iati_activities__iati_activity__location__exactness(exactness)

        return element

    '''atributes:
    gazetteer-ref:GEO

    tag:gazetteer-entry'''

    def iati_activities__iati_activity__location__gazetteer_entry(self, element):
        gazetteer_ref_code = element.attrib.get('gazetteer-ref')
        gazetteer_ref = self.gazetteer_agency_mapping.get(gazetteer_ref_code)
        code = element.text

        if not gazetteer_ref_code:
            raise RequiredFieldError(
                "location/gazetteer-entry",
                "gazetteer-ref",
                "required attribute missing")

        if not gazetteer_ref:
            raise FieldValidationError(
                "location/gazetteer-entry",
                "gazetteer-ref",
                "not found on the accompanying code list")

        if not code:
            raise RequiredFieldError(
                "location/gazetteer-entry",
                "text",
                "required element empty")

        location_id = E('location-id', code=code, vocabulary=gazetteer_ref)
        super(Parse, self).iati_activities__iati_activity__location__location_id(location_id)

        return element

    '''atributes:
    gazetteer-ref:GEO

    tag:gazetteer-entry'''

    def iati_activities__iati_activity__location__location_type(self, element):
        code = element.attrib.get('code')

        if not code:
            raise RequiredFieldError(
                "location/location-type",
                "code",
                "required attribute missing")

        feature_designation = E('feature-designation', code=code)
        super(Parse, self).iati_activities__iati_activity__location__feature_designation(
            feature_designation)

        return element
