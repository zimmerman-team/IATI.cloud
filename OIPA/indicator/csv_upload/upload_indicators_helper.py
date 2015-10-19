import uuid
from geodata.models import Country, City
from indicator.models import CsvUploadLog, IndicatorData, IndicatorDataValue


def get_countries():
    return Country.objects.all()


def get_cities():
    return City.objects.all()


def find_country(country_name, countries, iso2=None):
        """
        Mapping the country string, to a country in the database
        @param country_name string from csv document:
        @return: country from database or None if it could not map a country
        """

        #check is we are able to find the country based on the iso code
        if iso2:
            try:
                return Country.objects.get(code=iso2)
            except:
                pass

        if country_name:

            if len(country_name) == 2 and Country.objects.filter(code=country_name).exists():
                return Country.objects.get(code=country_name)

            country_name = country_name.lower().decode('utf8', errors='ignore').strip(' \t\n\r')

            for country in countries:
                if country_name in country.name.lower():
                    return country
                elif country.alt_name:
                    if country_name in country.alt_name.lower():
                        return country

        return None


def find_city(city_name, cities, country):
        """
        Mapping the city string, to a city in the database
        @param city_name string from csv document:
        @return: city from database or None if it could not map a country
        """

        if city_name and country:

            city_name = city_name.lower().decode('utf8', errors='ignore').strip(' \t\n\r')

            for city in cities:
                if city.country_id == country.code:
                    city_name_db = city.name.lower()
                    ascii_name_db = city.ascii_name
                    alt_name_db = city.alt_name
                    name_par_db = city.namepar

                    #cities have 4 names in the database, check them all
                    if city_name == city_name_db:
                        return city

                    if ascii_name_db:
                        if city_name == ascii_name_db.lower():
                            return city

                    if alt_name_db:
                        if city_name == alt_name_db.lower():
                            return city

                    if name_par_db:
                        if city_name == name_par_db.lower():
                            return city

        return None


def get_value(value_csv):
    value_csv = str(value_csv)\
        .replace(",", ".")\
        .replace(" ", "")\
        .replace("NULL", "")
    if not value_csv:
        return None
    return float(value_csv)


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


def save_city_data(city_from_db, selection_type_csv, indicator_from_db, year_csv, value_csv):

    if city_from_db and year_csv:

        indicator_data_from_db = IndicatorData.objects.get_or_create(
            indicator=indicator_from_db,
            selection_type=selection_type_csv,
            city=city_from_db)[0]

        # can't use get_or_create since indicator_data / year combo can exist with 'old' value
        if IndicatorDataValue.objects.filter(indicator_data=indicator_data_from_db, year=year_csv).exists():
            indicator_data_value_from_db = IndicatorDataValue.objects.filter(
                indicator_data=indicator_data_from_db,
                year=year_csv)[0]
            indicator_data_value_from_db.value = value_csv
        else:
            indicator_data_value_from_db = IndicatorDataValue(
                indicator_data=indicator_data_from_db,
                year=year_csv,
                value=value_csv)

        indicator_data_value_from_db.save()

        return True

    return False


def save_country_data(country_from_db, city_csv, selection_type_csv, year_csv, indicator_from_db, value_csv):

    if country_from_db and year_csv and not city_csv:
        indicator_data_from_db = IndicatorData.objects.get_or_create(
            indicator=indicator_from_db,
            selection_type=selection_type_csv,
            country=country_from_db)[0]

        # can't use get_or_create since indicator_data / year combo can exist with different 'old' value
        if IndicatorDataValue.objects.filter(indicator_data=indicator_data_from_db, year=year_csv).exists():
            indicator_data_value_from_db = IndicatorDataValue.objects.filter(
                indicator_data=indicator_data_from_db,
                year=year_csv)[0]
            indicator_data_value_from_db.value = value_csv
        else:
            indicator_data_value_from_db = IndicatorDataValue(
                indicator_data=indicator_data_from_db,
                year=year_csv,
                value=value_csv)

        indicator_data_value_from_db.save()

        return True

    return False