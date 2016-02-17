from django.contrib import admin

from geodata.models import City
from geodata.models import Country
from geodata.models import Region
from geodata.models import Adm1Region
from geodata.admin_models.admin1region_admin import Adm1RegionAdmin
from geodata.admin_models.city_admin import CityAdmin
from geodata.admin_models.country_admin import CountryAdmin
from geodata.admin_models.region_admin import RegionAdmin

admin.site.register(City, CityAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Adm1Region, Adm1RegionAdmin)
