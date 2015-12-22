from django.conf.urls import url
from django.contrib import admin
from geodata.models import *
from django.http import HttpResponse
from geodata.updaters import CountryUpdater, CityUpdater, Admin1RegionUpdater, RegionUpdater


class RegionAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = [
        '__unicode__',
        'code', 
        # 'region_vocabulary', 
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
        ru = RegionUpdater()
        ru.update_un_regions()
        return HttpResponse('Success')

    def import_unesco_regions(self, request):
        ru = RegionUpdater()
        ru.update_unesco_regions()
        return HttpResponse('Success')

    def update_region_center(self, request):
        ru = RegionUpdater()
        ru.update_center_longlat()
        return HttpResponse('Success')


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__', 'alt_name', 'capital_city', 'region', 'un_region', 'unesco_region', 'dac_country_code', 'iso3', 'alpha3', 'fips10', 'data_source']

    def get_urls(self):
        urls = super(CountryAdmin, self).get_urls()

        my_urls = [
            url(r'^update-polygon/$', self.admin_site.admin_view(self.update_polygon)),
            url(r'^update-country-center/$', self.admin_site.admin_view(self.update_country_center)),
            url(r'^update-regions/$', self.admin_site.admin_view(self.update_regions)),
            url(r'^update-country-identifiers/$', self.admin_site.admin_view(self.update_country_identifiers)),
            url(r'^update-alt-names/$', self.admin_site.admin_view(self.update_alt_names))
        ]
        return my_urls + urls

    def update_polygon(self, request):

        cu = CountryUpdater()
        cu.update_polygon_set()
        return HttpResponse('Success')

    def update_country_center(self, request):
        cu = CountryUpdater()
        cu.update_center_longlat()
        return HttpResponse('Success')

    def update_regions(self, request):
        cu = CountryUpdater()
        cu.update_regions()
        return HttpResponse('Success')

    def update_country_identifiers(self, request):
        cu = CountryUpdater()
        cu.update_identifiers()
        return HttpResponse('Success')

    def update_alt_names(self, request):
        cu = CountryUpdater()
        cu.update_alt_names()
        return HttpResponse('Success')


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['geoname_id', '__unicode__', 'ascii_name', 'alt_name', 'namepar']

    def get_urls(self):
        urls = super(CityAdmin, self).get_urls()

        my_urls = [
            url(r'^update-cities/$', self.admin_site.admin_view(self.update_cities))
        ]
        return my_urls + urls

    def update_cities(self, request):
        cu = CityUpdater()
        cu.update_cities()
        return HttpResponse('Success')


class Adm1RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__', 'adm1_code', 'country', 'type', 'admin']

    def get_urls(self):
        urls = super(Adm1RegionAdmin, self).get_urls()

        my_urls = [
            url(r'^update-adm1-regions/$', self.admin_site.admin_view(self.update_adm1_regions))
        ]
        return my_urls + urls

    def update_adm1_regions(self, request):
        adm1u = Admin1RegionUpdater()
        adm1u.update_all()
        return HttpResponse('Success')



    def change_view(self, request, object_id, extra_context=None):
        self.exclude = ('polygon', 'center_location', )
        return super(Adm1RegionAdmin, self).change_view(request, object_id, extra_context=None)



admin.site.register(City, CityAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Adm1Region, Adm1RegionAdmin)
