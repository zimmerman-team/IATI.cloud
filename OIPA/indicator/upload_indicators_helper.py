from geodata.models import Country, City


def get_countries():
    return Country.objects.all()

def get_cities():
    return City.objects.all()

def find_country(country_name, countries):
        """
        Mapping the country string, to a country in the database
        @todo create a more optimized solution for this, it only matches an exact string, or the first 8 or last 8 characters
        @param country_name string from csv document:
        @return: country from database or False if it could not map a country
        """
        #getting countries from database
        for country in countries:
            country_name_db = country.name
            if country_name.decode('utf8') in country_name_db or country_name.decode('utf8')[:8] in country_name_db or country_name.decode('utf8')[-8:] in country_name_db:
                return country
        return False

def find_city(city_name, cities):
        """
        Mapping the country string, to a country in the database
        @todo create a more optimized solution for this, it only matches an exact string, or the first 8 or last 8 characters
        @param country_name string from csv document:
        @return: country from database or False if it could not map a country
        """
        #getting countries from database
        for city in cities:
            city_name = city_name.decode('utf8')
            city_name_db = city.name
            ascii_name_db = city.ascii_name
            alt_name_db = city.alt_name
            name_par_db = city.namepar

            if city_name in city_name_db or city_name[:8] in city_name_db or city_name[-8:] in city_name_db:
                return city
        return False