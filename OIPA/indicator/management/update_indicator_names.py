# Django specific
from django.core.management.base import BaseCommand
from data.models import Country
from data.models.common import UnHabitatIndicatorCountry, IndicatorData, Indicator
from data.models.constants import COUNTRY_LOCATION


class Command(BaseCommand):
    option_list = BaseCommand.option_list
#Urban population
#Total population
#Access to bottled water
#Access to composting toilet
#Connection to electricity
#Deprivation [This is not an indicator]
#Female enrollment in primary education
#Male enrollment in primary education
#Access to telephone
#Access to improved flooring
#Access to improved flush toilet
#Access to improved pit latrine
#Access to improved spring/surface water
#Access to improved toilet
#Access to improved water
#Access to piped water
#Access to slab or covered pit latrine
#Access to pit latrine without slab
#Rural population
#Urban population
#Urban population percentage [How is this different to the previous one?]
#Total population
#Access to protected well
#Access to public tap/pump/borehole [can't see this one in the database]
#Access to pump or borehole [how is this different from the previous one]
#Access to rainwater
#Proportion of slum dwellers
#Access to sufficient living conditions
#Under five mortality rate
#Urban population [is this repeated?]
#Slum population [is this repeated?]
    mapping_names = {'avg_annual_rate_change_percentage_urban' : {'name' : 'Annual urban population change %' , 'type_data' : 'p'},
                                                   'avg_annual_rate_change_total_population' : {'name' :'Annual population change %','type_data' : 'p'},

                                                    'bottle_water' : {'name' :'Access to bottled water','type_data' : 'p'},
                                                    'composting_toilet' : {'name' : 'Access to composting toilet','type_data' : 'p' },
                                                    'connection_to_electricity' : {'name' : 'Connection to electricity','type_data' : 'p' },
                                                    'deprivation' : {'name' : 'Is not an indicator','type_data' : 'p' },
                                                    'enrollment_female_primary_education' : {'name' : 'Female enrollment in primary education','type_data' : 'p' },
                                                    'enrollment_male_primary_education' : {'name' : 'Male enrollment in primary education','type_data' : 'p' },
                                                    'has_telephone' : {'name' : 'Access to telephone','type_data' : 'p' },
                                                    'improved_floor' : {'name' : 'Access to improved flooring','type_data' : 'p' },
                                                    'improved_flush_toilet' : {'name' : 'Access to improved flush toilet','type_data' : 'p' },
                                                    'improved_pit_latrine' : {'name' : 'Access to improved pit latrine','type_data' : 'p' },
                                                    'improved_spring_surface_water' : {'name' : 'Access to improved spring/surface water','type_data' : 'p' },
                                                    'improved_toilet' : {'name' : 'Access to improved toilet','type_data' : 'p' },
                                                    'improved_water' : {'name' : 'Access to improved water','type_data' : 'p' },
                                                    'piped_water' : {'name' : 'Access to piped water','type_data' : 'p' },
                                                    'pit_latrine_with_slab_or_covered_latrine' : {'name' : 'Access to slab or covered pit latrine','type_data' : 'p' },
                                                    'pit_latrine_without_slab' : {'name' : 'Access to pit latrine without slab','type_data' : 'p' },
                                                    'pop_rural_area' : {'name' : 'Rural population area','type_data' : '1000' },
                                                    'pop_urban_area' : {'name' : 'Urban population area','type_data' : '1000' },
                                                    'pop_urban_percentage' : {'name' : 'Urban population %','type_data' : 'p' },
                                                    'population' : {'name' : 'Total population','type_data' : '1000' },
                                                    'protected_well' : {'name' : 'Access to protected well','type_data' : 'p' },
                                                    'public_tap_pump_borehole' : {'name' : 'Access to public tap/pump/borehole','type_data' : 'p' },
                                                    'pump_borehole' : {'name' : 'Access to pump/borehole','type_data' : 'p' },
                                                    'rainwater' : {'name' : 'Access to rainwater','type_data' : 'p' },
                                                    'slum_proportion_living_urban' : {'name' : 'Slum proportion living in urban area\'s','type_data' : 'p' },
                                                    'sufficient_living' : {'name' : 'Access to sufficient living','type_data' : 'p' },
                                                    'under_five_mortality_rate' : {'name' : 'Under five mortality rate','type_data' : 'p' },
                                                    'urban_population' : {'name' : 'Urban population','type_data' : '1000' },
                                                    'urban_slum_population' : {'name' : 'Urban slum population','type_data' : '1000'},
                                                    'cpi_5_dimensions' : {'name' :'5 dimensions','type_data' : 'p'},
                                                    'cpi_4_dimensions' : {'name' :'4 dimensions','type_data' : 'p'},
                                                    'cpi_productivity_index' : {'name' :'Productivity index','type_data' : 'p' },
                                                    'cpi_quality_of_live_index' : {'name' :'Quality of life index','type_data' : 'p'},
                                                    'cpi_infrastructure_index' : {'name' :'Infrastructure Development index','type_data' : 'p'},
                                                    'cpi_environment_index' : {'name' :'Environmental Sustainability index','type_data' : 'p'},
                                                    'cpi_equity_index' : {'name' :'Equity Index','type_data' : 'p'}
    }

    def handle(self, *args, **options):
        for i in Indicator.objects.all():
            try:
                i.friendly_label = self.mapping_names[i.name]['name']
                i.type_data = self.mapping_names[i.name]['type_data']
                i.save()
            except:
                pass
#            print self.mapping_names[i.name]



