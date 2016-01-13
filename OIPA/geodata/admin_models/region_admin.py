import ujson
import os
import os.path

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.gis.geos import fromstr

from geodata.models import Country
from geodata.models import Region
from iati_vocabulary.models import RegionVocabulary


class RegionAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = [
        '__unicode__',
        'code',
        'parental_region'
    ]

    def get_urls(self):
        urls = super(RegionAdmin, self).get_urls()

        my_urls = [
            url(r'^import-un-regions/$', self.admin_site.admin_view(self.import_un_regions)),
            url(r'^import-unesco-regions/$', self.admin_site.admin_view(self.import_unesco_regions)),
            url(r'^update-region-center/$', self.admin_site.admin_view(self.update_region_center))
        ]
        return my_urls + urls

    def import_un_regions(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/un_region_codes.json"

        json_data = open(location)
        un_region_codes = ujson.load(json_data)

        times = 0
        while times < 2:
            times += 1
            for cr in un_region_codes["territorycontainment"]["group"]:
                try:
                    type = cr['type']
                    contains = cr['contains']
                    region_un_name = cr['name']

                    the_region = None

                    if Region.objects.filter(code=type).exists():
                        the_region = Region.objects.get(code=type)
                        the_region.name = region_un_name
                    else:
                        the_region_voc = RegionVocabulary.objects.get(code=2)
                        the_region = Region(code=type, name=region_un_name, region_vocabulary=the_region_voc, parental_region=None)

                    the_region.save()

                    countries_or_regions = contains.split(" ")
                    try:
                        int(countries_or_regions[0])

                        for cur_region in countries_or_regions:
                            if Region.objects.filter(code=cur_region).exists():
                                cur_region_obj = Region.objects.get(code=cur_region)
                                cur_region_obj.parental_region = the_region
                                cur_region_obj.save()

                    except:
                        for cur_country in countries_or_regions:
                            if Country.objects.filter(code=cur_country).exists():
                                the_country = Country.objects.get(code=cur_country)
                                the_country.un_region = the_region
                                the_country.save()

                except Exception as e:
                    print "error in update_country_regions" + str(type)
                    print e.args
        json_data.close()
        return HttpResponse('Success')

    def import_unesco_regions(self, request):
        """
        This code will create/update unesco regions and update the country -> region mapping
        """
        import os
        import ujson
        from geodata.models import Region
        from iati_vocabulary.models import RegionVocabulary

        base = os.path.dirname(os.path.abspath(__file__))

        location = base + '/../data_backup/unesco_regions.json'
        json_data = open(location)
        unesco_regions = ujson.load(json_data)
        json_data.close()

        location_map = base + '/../data_backup/unesco_country_region_mapping.json'
        json_data_map = open(location_map)
        unesco_mapping = ujson.load(json_data_map)
        json_data_map.close()

        #save regions and put in list
        regions = []
        region_vocabulary = RegionVocabulary.objects.get_or_create(
            code=999,
            name='UNESCO')[0]

        for region_id, info in unesco_regions.iteritems():

            center_location_string = 'POINT(' + info['longitude'] + ' ' + info['latitude'] + ')'
            center_location = fromstr(
                center_location_string,
                srid=4326)
            region = Region.objects.get_or_create(
                code=region_id,
                defaults={
                    'name': info['name'],
                    'region_vocabulary': region_vocabulary,
                    'parental_region': None,
                    'center_longlat': center_location})[0]
            regions.append(region)

        # save country -> region mapping
        for line in unesco_mapping:

            region_id = line["UNESCO Region Code"]
            country_id = line["Country ID"]
            country = Country.objects.get(code=country_id)
            for region in regions:
                if region.code == region_id:
                    country.unesco_region = region
                    country.save()
        return HttpResponse('Success')

    def update_region_center(self, request):
        base = os.path.dirname(os.path.abspath(__file__))
        location = base + "/../data_backup/region_center_locations.json"

        json_data = open(location)
        region_centers = ujson.load(json_data)
        for r in region_centers:
            if Region.objects.filter(code=r).exists():
                current_region = Region.objects.get(code=r)

                point_loc_str = ''.join([
                    'POINT(',
                    str(region_centers[r]["longitude"]),
                    ' ',
                    str(region_centers[r]["latitude"]),
                    ')'])

                longlat = fromstr(point_loc_str, srid=4326)
                current_region.center_longlat = longlat
                current_region.save()

        json_data.close()
        return HttpResponse('Success')


