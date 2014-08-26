# Data specific
from geodata.data_backup.country_data import countryData

class CustomCallHelper():

    def make_where_query(self, values, name):
        query = ''
        if values:
            if not values[0]:
                return None

            for v in values:
                query += '  ' + name + ' = "' + v +'" OR'
            query = query[:-2]
        return query

    def get_and_query(self, request, parameter, queryparameter):

        filters = request.GET.get(parameter, None)
        if filters:
            query = self.make_where_query(values=filters.split(','), name=queryparameter)
            query += ') AND ('
        else:
            query = ''
        return query

    def make_year_where_query(self, values, name):
        query = ''
        if values:
            if not values[0]:
                return None

            for v in values:
                query += '  YEAR(' + name + ') = "' + v + '" OR'
            query = query[:-2]
        return query

    def get_year_and_query(self, request, parameter, queryparameter):

        filters = request.GET.get(parameter, None)
        if filters:
            query = self.make_year_where_query(values=filters.split(','), name=queryparameter)
            query += ') AND ('
        else:
            query = ''
        return query

    def get_fields(self, cursor):
        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
        return results

    def get_filter_query(self, filters):
        q= ''

        for f in filters:
            if f[f.keys()[0]]:
                values = f[f.keys()[0]].split(',')
            else:
                values = None
            q += self.make_where_query(values=values, name=f.keys()[0]) + ') and ('

        q = q.replace(' and ()', '')
        q = q[:-5]
        q = " AND (" + q
        try:
            q[8]
            return q
        except IndexError:
            return ''

    def find_polygon(self, iso2):
        polygon = None
        for k in countryData['features']:
            try:
                if k['properties']['iso2'] == iso2:
                    polygon = k['geometry']
            except KeyError:
                pass
        if not polygon:
            polygon = {
                "type" : "Polygon",
                "coordinates" : []
            }

        return polygon