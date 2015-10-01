from IATI_1_05 import Parse as IATI_105_Parser
from iati import models
from geodata.models import Country, Region
import dateutil.parser
from lxml.builder import E

class Parse(IATI_105_Parser):

    VERSION = '1.05' # version of iati standard

    # maps to geographic vocabulary
    gazetteer_agency_mapping = {
        "1": "G1",
        # "2": "",
        "3": "G2",
    }

    '''atributes:
	code:ADM2
	{http://www.w3.org/XML/1998/namespace}lang:en

    tag:location-type'''
    def iati_activities__iati_activity__location__administrative(self,element):
        country = element.attrib.get('country')
        adm1 = element.attrib.get('adm1')
        adm2 = element.attrib.get('adm2')
        
        if country:
            elem = E('administrative', code=country, vocabulary="A4") # ISO Country (3166-1 alpha-2)
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        if adm1:
            elem = E('administrative', code=country, vocabulary="A2", level="1") # UN Second Administrative Level Boundary Project
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        if adm2:
            elem = E('administrative', code=country, vocabulary="A2", level="2") # UN Second Administrative Level Boundary Project
            super(Parse, self).iati_activities__iati_activity__location__administrative(elem)

        return element

    '''atributes:
	latitude:36.79256
	longitude:68.84385
	precision:3

    tag:coordinates'''
    def iati_activities__iati_activity__location__coordinates(self,element):
        latitude = element.attrib.get('latitude')
        longitude = element.attrib.get('longitude')
        precision = element.attrib.get('precision')
         
        if not latitude: raise self.RequiredFieldError("latitude", "location_coordinates: latitude is required")
        if not longitude: raise self.RequiredFieldError("longitude", "location_coordinates: longitude is required")

        point = E('point')
        super(Parse, self).iati_activities__iati_activity__location__point(point)
        pos = E('pos', latitude + ' ' + longitude) # ISO Country (3166-1 alpha-2)
        super(Parse, self).iati_activities__iati_activity__location__point__pos(pos)

        if precision:
            if precision != "1": precision = "2" # Everything but "Exact" is "Approximate"
            exactness = E('exactness', code=precision)
            super(Parse, self).iati_activities__iati_activity__location__exactness(exactness)

        return element

    '''atributes:
	gazetteer-ref:GEO

    tag:gazetteer-entry'''
    def iati_activities__iati_activity__location__gazetteer_entry(self,element):
        gazetteer_ref = self.gazetteer_agency_mapping.get(element.attrib.get('gazetteer-ref'))
        code = element.text

        if not gazetteer_ref: raise self.RequiredFieldError("gazeteer_ref", "gazeteer_entry: ref is required")
        if not code: raise self.RequiredFieldError("gazeteer_ref", "gazeteer_entry: text is required")

        location_id = E('location-id', code=code, vocabulary=gazetteer_ref)
        super(Parse, self).iati_activities__iati_activity__location__location_id(location_id)

        return element 

    '''atributes:
	gazetteer-ref:GEO

    tag:gazetteer-entry'''
    def iati_activities__iati_activity__location__location_type(self,element):
        code = element.attrib.get('code')

        if not code: raise self.RequiredFieldError("location_type", "location_type: code is required")

        feature_designation = E('feature-designation', code=code)
        super(Parse, self).iati_activities__iati_activity__location__feature_designation(feature_designation)

        return element 
