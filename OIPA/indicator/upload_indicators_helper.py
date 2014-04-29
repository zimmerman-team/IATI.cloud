import uuid
from geodata.models import Country, City
from indicator.models import CsvUploadLog, IndicatorData


def get_countries():
    return Country.objects.all()

def get_cities():
    return City.objects.all()

def find_country(country_name, countries, iso2=None):
        """
        Mapping the country string, to a country in the database
        @todo create a more optimized solution for this, it only matches an exact string, or the first 8 or last 8 characters
        @param country_name string from csv document:
        @return: country from database or False if it could not map a country
        """

        #check is we are able to find the country based on the iso code
        if iso2:
            try:
                return Country.objects.get(code=iso2)
            except:
                pass

        #getting countries from database
        try:
            if country_name:
                for country in countries:
                    country_name_db = country.name.lower()
                    country_name = country_name.lower()
                    if country_name.decode('utf8') in country_name_db or country_name.decode('utf8')[:8] in country_name_db or country_name.decode('utf8')[-8:] in country_name_db:
                        return country

            else:
                return None
        except:
            return None

        return None


def find_city(city_name, cities):
        """
        Mapping the country string, to a country in the database
        @todo create a more optimized solution for this, it only matches an exact string, or the first 8 or last 8 characters
        @param country_name string from csv document:
        @return: country from database or False if it could not map a country
        """
        #getting countries from database
        try:
            if city_name:
                for city in cities:
                    city_name = city_name.lower()

                    city_name = city_name.decode('utf8')
                    city_name_db = city.name.lower()

                    ascii_name_db = city.ascii_name
                    alt_name_db = city.alt_name
                    name_par_db = city.namepar

                    if city_name in city_name_db or city_name[:8] in city_name_db or city_name[-8:] in city_name_db:
                        return city
            else:
                return None
        except:
            return None

        return None

def get_value(value_csv):
    value = None
    value_csv = value_csv.replace(' ', '')
    if value_csv:
        #check if the value is a decimal
        value = value_csv
        if '.' in value:
            value = value.replace('.', '')
        if ',' in value[-4: -1]:
            value = value.replace(',', '.')

        return float(value)



    else:
        value = None
    return value


def save_log(
        file,
        uploaded_by_user,
        cities_not_found,
        countries_not_found,
        total_cities_found,
        total_countries_found,
        total_countries_not_found,
        total_cities_not_found,
        total_items_saved):

    log = CsvUploadLog()
    log.upload = file
    log.uploaded_by = uploaded_by_user
    log.slug = uuid.uuid4()
    try:
        log.cities_not_found = unicode(', '.join(cities_not_found), errors='ignore')
        log.countries_not_found = unicode(', '.join(countries_not_found), errors='ignore')
    except:
        log.cities_not_found = ', '.join(cities_not_found)
        log.countries_not_found = ', '.join(countries_not_found)

    log.total_cities_found = total_cities_found.__len__()
    log.total_countries_found = total_countries_found.__len__()
    log.total_countries_not_found = total_countries_not_found.__len__()
    log.total_cities_not_found = total_cities_not_found.__len__()
    log.total_items_saved = total_items_saved
    log.save()
    return log

def save_city_data(city_from_db, country_from_db, selection_type_csv, indicator_from_db, year_csv, value_csv):
    try:
        if city_from_db:
            #if the indicator data a selection type contains than we need to store that correctly
            if selection_type_csv:
                indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, selection_type=selection_type_csv, city=city_from_db)[0]
            else:
                indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, city=city_from_db)[0]

            #some city files also contain the country, so when this happens we also store it
            if country_from_db:
                indicator_data_from_db.country = country_from_db

            indicator_data_from_db.city = city_from_db
            #todo get region from db

            indicator_data_from_db.value = get_value(value_csv=value_csv)
            #todo add year range to model IndicatorData
            #if year_range_csv:
            #    indicator_data_from_db.year_range = year_range_csv
            indicator_data_from_db.save()
            return True
        else:
            return False
    except:
        #todo we need to know what is going wrong. We need to find the errors and give it back to the user.
        return False

def save_country_data(country_from_db, city_csv, selection_type_csv, year_csv, indicator_from_db, value_csv):
    try:
        if country_from_db and not city_csv:
            if selection_type_csv:
                indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, selection_type=selection_type_csv, country=country_from_db)[0]
            else:
                indicator_data_from_db = IndicatorData.objects.get_or_create(year=year_csv, indicator=indicator_from_db, country=country_from_db)[0]
            #todo get region from db
            indicator_data_from_db.value = get_value(value_csv=value_csv)


            #todo add year range to model IndicatorData
            #if year_range_csv:
            #    indicator_data_from_db.year_range = year_range_csv
            indicator_data_from_db.save()
            return True
        else:
            return False
    except:
        #todo we need to know what is going wrong. We need to find the errors and give it back to the user.
        return False