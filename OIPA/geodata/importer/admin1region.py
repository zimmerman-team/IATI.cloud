from django.contrib.gis.geos import fromstr

from geodata.models import Country
from geodata.models import Adm1Region
from geodata.importer.common import get_json_data


class Adm1RegionImport():
    """
    Wrapper class for all import methods used on the Adm1Region model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_from_json(self):
        adm1_regions = self.get_json_data("/../data_backup/admin_1_regions.json")

        for r in adm1_regions['features']:

            the_adm1_region = Adm1Region()

            p = r["properties"]

            field_list = [
                'adm1_code',
                'OBJECTID_1',
                'diss_me',
                'adm1_cod_1',
                'wikipedia',
                'adm0_sr',
                'name',
                'name_alt',
                'name_local',
                'type',
                'type_en',
                'code_local',
                'code_hasc',
                'note',
                'hasc_maybe',
                'region',
                'region_cod',
                'provnum_ne',
                'gadm_level',
                'check_me',
                'scalerank',
                'datarank',
                'abbrev',
                'postal',
                'area_sqkm',
                'sameascity',
                'labelrank',
                'featurecla',
                'name_len',
                'mapcolor9',
                'mapcolor13',
                'fips',
                'fips_alt',
                'woe_id',
                'woe_label',
                'woe_name',
                'sov_a3',
                'adm0_a3',
                'adm0_label',
                'admin',
                'geonunit',
                'gu_a3',
                'gn_id',
                'gn_name',
                'gns_id',
                'gns_name',
                'gn_level',
                'gn_region',
                'gn_a1_code',
                'region_sub',
                'sub_code',
                'gns_level',
                'gns_lang',
                'gns_adm1',
                'gns_region']

            for field in field_list:
                if p.get(field):
                    setattr(the_adm1_region, field, p.get(field))

            if p.get('iso_a2'):
                if Country.objects.filter(code=p.get('iso_a2')).exists():
                    the_country = Country.objects.get(code=p.get('iso_a2'))
                    the_adm1_region.country = the_country
                elif p.get('admin') and p.get('admin') == "Kosovo":
                    the_country = Country.objects.get(code="XK")
                    the_adm1_region.country = the_country

            if p.get('longitude') and p.get('latitude'):
                try:
                    longitude = str(p.get('longitude'))
                    latitude = str(p.get('latitude'))
                    point_loc_str = 'POINT(' + longitude + ' ' + latitude + ')'
                    the_adm1_region.center_location = fromstr(point_loc_str, srid=4326)
                except KeyError:
                    print "Admin 1 region with code %s has an illegal center location..." % the_adm1_region.adm1_code

            the_adm1_region.polygon = r["geometry"].get('coordinates')
            the_adm1_region.geometry_type = r["geometry"].get('type')

            the_adm1_region.save()