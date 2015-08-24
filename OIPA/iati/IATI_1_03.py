from IATI_1_05 import Parse as IATI_105_Parser
from iati import models
from geodata.models import Country, Region
import dateutil.parser

class Parse(IATI_105_Parser):

    VERSION = '1.05'#version of iati standard

    '''atributes:
	code:ADM2
	{http://www.w3.org/XML/1998/namespace}lang:en

    tag:location-type'''
    def iati_activities__iati_activity__location__location_type(self,element):
        model = self.get_func_parent_model()
        location_type = self.cached_db_call_no_version(models.LocationType,element.attrib.get('code'))
        model.type = location_type
        #store element 
        return element

    '''atributes:
	latitude:36.79256
	longitude:68.84385
	precision:3

    tag:coordinates'''
    def iati_activities__iati_activity__location__coordinates(self,element):
        model = self.get_func_parent_model()
        latitude = element.attrib.get('latitude')
        longitude = element.attrib.get('longitude')
        #store element 
        model.point_pos = latitude+' '+longitude
        return element

    '''atributes:
	gazetteer-ref:GEO

    tag:gazetteer-entry'''
    def iati_activities__iati_activity__location__gazetteer_entry(self,element):
        model = self.get_func_parent_model()
        model.gazetteer_entry = element.text
        model.gazetteer_ref = self.cached_db_call_no_version(models.GazetteerAgency,element.attrib.get('gazetteer_-ef'))
        #store element 
        return element
