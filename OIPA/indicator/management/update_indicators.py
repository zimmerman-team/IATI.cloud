# Django specific
from django.core.management.base import BaseCommand
from data.models import Country
from data.models.common import UnHabitatIndicatorCountry, IndicatorData, Indicator, TypeDeprivationCountry
from data.models.constants import COUNTRY_LOCATION


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        get_indicator_data = False
        try:
            if args[0]:

                get_indicator_data = True
        except IndexError:
            get_indicator_data = False
        for country in Country.objects.all():

            try:
                if not country.latitude == COUNTRY_LOCATION[country.iso]['latitude'] or not country.iso2 == country.iso:
                    country.latitude = COUNTRY_LOCATION[country.iso]['latitude']
                    country.longitude = COUNTRY_LOCATION[country.iso]['longitude']
                    country.iso2 = country.iso
                    country.save()
                    print "Country %s has been updated " % country.iso
            except KeyError:
                pass

            if args[0] == 'multiple':
                multiple_indicators = TypeDeprivationCountry.objects.filter(is_matrix=True)
                for m in multiple_indicators:
                    print m

            if args[0] == 'single':
                unhabitat_indicators = UnHabitatIndicatorCountry.objects.filter(country=country)
                for i in unhabitat_indicators:
                    indicator, _ = Indicator.objects.get_or_create(name='population')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.population, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='urban_slum_population')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.urban_slum_population, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='avg_annual_rate_change_percentage_urban')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.avg_annual_rate_change_percentage_urban, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='avg_annual_rate_change_total_population')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.avg_annual_rate_change_total_population, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='bottle_water')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.bottle_water, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='composting_toilet')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.composting_toilet, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='connection_to_electricity')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.connection_to_electricity, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='enrollment_female_primary_education')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.enrollment_female_primary_education, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='enrollment_male_primary_education')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.enrollment_male_primary_education, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='has_telephone')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.has_telephone, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_floor')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_floor, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_flush_toilet')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_flush_toilet, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_pit_latrine')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_pit_latrine, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_spring_surface_water')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_spring_surface_water, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_water')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_water, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='piped_water')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.piped_water, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pit_latrine_with_slab_or_covered_latrine')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pit_latrine_with_slab_or_covered_latrine, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pit_latrine_without_slab')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pit_latrine_without_slab, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pop_rural_area')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pop_rural_area, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='protected_well')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.protected_well, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pop_urban_area')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pop_urban_area, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='improved_toilet')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.improved_toilet, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pop_urban_percentage')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pop_urban_percentage, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='public_tap_pump_borehole')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.public_tap_pump_borehole, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='pump_borehole')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.pump_borehole, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='rainwater')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.rainwater, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='slum_proportion_living_urban')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.slum_proportion_living_urban, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='sufficient_living')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.sufficient_living, year=i.year)

                    indicator, _ = Indicator.objects.get_or_create(name='under_five_mortality_rate')
                    IndicatorData.objects.get_or_create(indicator=indicator, country=country, value=i.under_five_mortality_rate, year=i.year)


