# Django specific
from django.core.management.base import BaseCommand
from geodata.models import Country
from indicator.models import Indicator
from indicator.models.common import UnHabitatIndicatorCountry, IndicatorCityData, Indicator, City, UnHabitatIndicatorCity



class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
#        for city in City.objects.all():

        unhabitat_indicators = UnHabitatIndicatorCity.objects.filter(year=2012)
        for i in unhabitat_indicators:
            indicator, _ = Indicator.objects.get_or_create(name='cpi_5_dimensions')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_5_dimensions, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_4_dimensions')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_4_dimensions, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_productivity_index')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_productivity_index, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_quality_of_live_index')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_quality_of_live_index, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_infrastructure_index')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_infrastructure_index, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_environment_index')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_environment_index, year=i.year)

            indicator, _ = Indicator.objects.get_or_create(name='cpi_equity_index')
            IndicatorCityData.objects.get_or_create(indicator=indicator, city=i.city, value=i.cpi_equity_index, year=i.year)


               


