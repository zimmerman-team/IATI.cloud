from django.contrib import admin

from geodata.models import Adm1Region, Country, Region


class Adm1RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = [
        '__unicode__',
        'adm1_code',
        'country',
        'type',
        'admin']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('polygon', 'center_location', )
        return super(Adm1RegionAdmin, self).change_view(
            request, object_id, form_url, extra_context)


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = [
        '__unicode__',
        'alt_name',
        'region',
        'un_region',
        'unesco_region',
        'dac_country_code',
        'iso3',
        'alpha3',
        'fips10',
        'data_source']


class RegionAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = [
        '__unicode__',
        'code',
        'parental_region'
    ]


admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Adm1Region, Adm1RegionAdmin)
