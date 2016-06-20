from django.contrib.gis.geos import fromstr
from geodata.models import Region
from geodata.importer.common import get_json_data


class RegionImport():
    """
    Wrapper class for all import methods used on the Region model
    """
    def __init__(self):
        self.get_json_data = get_json_data

    def update_region_center(self):
        region_centers = self.get_json_data("/../data_backup/region_center_locations.json")
        for r in region_centers:
            if Region.objects.filter(code=r).exists():
                current_region = Region.objects.get(code=r)
                point_loc_str = 'POINT(%s %s)' % (str(region_centers[r]["longitude"]), str(region_centers[r]["latitude"]))
                longlat = fromstr(point_loc_str, srid=4326)
                current_region.center_longlat = longlat
                current_region.save()

