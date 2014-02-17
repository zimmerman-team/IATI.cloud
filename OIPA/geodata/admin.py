from django.conf.urls import patterns
from django.contrib import admin
from geodata.models import *
from django.http import HttpResponse
from geodata.admin_tools import AdminTools


class RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__','code', 'region_vocabulary', 'parental_region']

    def get_urls(self):
        urls = super(RegionAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^import-un-regions/$', self.admin_site.admin_view(self.import_un_regions))
        )
        return my_urls + urls

    def import_un_regions(self, request):
        admTools = AdminTools()
        admTools.import_un_regions()
        return HttpResponse('Success')


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__', 'capital_city', 'region']

    def get_urls(self):
        urls = super(CountryAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-polygon/$', self.admin_site.admin_view(self.update_polygon)),
            (r'^update-country-center/$', self.admin_site.admin_view(self.update_country_center)),
            (r'^update-regions/$', self.admin_site.admin_view(self.update_regions)),
            (r'^update-country-identifiers/$', self.admin_site.admin_view(self.update_country_identifiers))
        )
        return my_urls + urls

    def update_polygon(self, request):
        admTools = AdminTools()
        admTools.update_polygon_set()
        return HttpResponse('Success')

    def update_country_center(self, request):
        admTools = AdminTools()
        admTools.update_country_center()
        return HttpResponse('Success')

    def update_regions(self, request):
        admTools = AdminTools()
        admTools.update_country_regions()
        return HttpResponse('Success')

    def update_country_identifiers(self, request):
        admTools = AdminTools()
        admTools.update_country_identifiers()
        return HttpResponse('Success')


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['geoname_id', '__unicode__', 'ascii_name', 'alt_name', 'namepar']

    def get_urls(self):
        urls = super(CityAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-cities/$', self.admin_site.admin_view(self.update_cities))
        )
        return my_urls + urls

    def update_cities(self, request):
        admTools = AdminTools()
        admTools.update_cities()
        return HttpResponse('Success')


class Adm1RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['__unicode__', 'adm1_code', 'country', 'type', 'admin']

    def get_urls(self):
        urls = super(Adm1RegionAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-adm1-regions/$', self.admin_site.admin_view(self.update_adm1_regions))
        )
        return my_urls + urls

    def update_adm1_regions(self, request):
        admTools = AdminTools()
        admTools.update_adm1_regions()
        return HttpResponse('Success')


admin.site.register(City, CityAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Adm1Region, Adm1RegionAdmin)
