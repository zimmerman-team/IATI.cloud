import csv
import StringIO
from tastypie.serializers import Serializer
import string

class CsvSerializer(Serializer):
    formats = ['json', 'xml', 'csv']
    content_types = {
        'json': 'application/json',
        'xml': 'application/xml',
        'csv': 'text/csv',
    }


    def to_csv(self, data, options=None):
        options = options or {}

        data = self.to_simple(data, options)

        raw_data = StringIO.StringIO()
        first = True

        try:

            if "meta" in data.keys(): #if multiple objects are returned
                objects = data.get("objects")

                for value in objects:

                    test = self.set_data(value)

                    if first:
                        writer = csv.DictWriter(raw_data, test.keys(), delimiter=";", quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                        writer.writeheader()
                        writer.writerow(test)
                        first=False
                    else:
                        writer.writerow(test)
            else:
                test = {}
                self.flatten("", data, test)
                if first:
                    writer = csv.DictWriter(raw_data, test.keys(), delimiter=";", quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                    writer.writeheader()
                    writer.writerow(test)
                    first=False
                else:
                    writer.writerow(test)
            CSVContent=raw_data.getvalue()
            return CSVContent

        except Exception as e:
            print e

    def set_data(self, data):

        # set keys
        column_dict = {'activity_scope': None, 'activity_status': None, 'total_budget': None, 'collaboration_type': None, 'countries': None, 'default_aid_type': None, 'default_finance_type': None, 'default_flow_type': None, 'descriptions': None, 'titles': None, 'end_actual': None, 'end_planned': None, 'start_actual': None, 'start_planned': None, 'iati_identifier': None, 'last_updated_datetime': None, 'participating_organisations': None, 'participating_org_accountable': None, 'participating_org_extending': None, 'participating_org_funding': None, 'participating_org_implementing': None}

        try:

            # fill keys
            for dest_key in column_dict:

                if dest_key in data.keys():

                    if isinstance(data[dest_key], list):

                        if dest_key == "participating_organisations":

                            participating_org_accountable = []
                            participating_org_extending = []
                            participating_org_funding = []
                            participating_org_implementing = []

                            for org in data[dest_key]:

                                if not org["name"]:
                                    continue

                                if 'role_id' in org:

                                    if org["role_id"] == "Accountable":
                                        participating_org_accountable.append(org["name"])
                                    if org["role_id"] == "Extending":
                                        participating_org_extending.append(org["name"])
                                    if org["role_id"] == "Funding":
                                        participating_org_funding.append(org["name"])
                                    if org["role_id"] == "Implementing":
                                        participating_org_implementing.append(org["name"])

                            column_dict["participating_org_accountable"] = ", ".join(participating_org_accountable)
                            column_dict["participating_org_extending"] = ", ".join(participating_org_extending)
                            column_dict["participating_org_funding"] = ", ".join(participating_org_funding)
                            column_dict["participating_org_implementing"] = ", ".join(participating_org_implementing)

                        if dest_key == "countries":

                            countries = []

                            for country in data[dest_key]:
                                countries.append(country["name"])
                            column_dict[dest_key] = ", ".join(countries)

                        if dest_key == "regions":

                            regions = []

                            for region in data[dest_key]:
                                regions.append(region["name"])
                            column_dict[dest_key] = ", ".join(regions)

                        if dest_key == "sectors":

                            sectors = []

                            for sector in data[dest_key]:
                                sectors.append(sector["name"])
                            column_dict[dest_key] = ", ".join(sectors)


                        if dest_key == "titles":

                            titles = []

                            for title in data[dest_key]:
                                if title["title"]:
                                    titles.append(title["title"])
                            column_dict[dest_key] = ", ".join(titles)

                        if dest_key == "descriptions":

                            descriptions = []

                            for description in data[dest_key]:
                                if description["description"]:
                                    descriptions.append(description["description"])
                            column_dict[dest_key] = ", ".join(descriptions)

                        continue

                    if isinstance(data[dest_key], dict):

                        if "name" in data[dest_key]:
                            column_dict[dest_key] = data[dest_key]["name"]
                        continue

                    column_dict[dest_key] = data[dest_key]


            del column_dict["participating_organisations"]

            for dest_key in column_dict:
                if column_dict[dest_key]:
                    column_dict[dest_key] = column_dict[dest_key].encode('utf-8', 'ignore')


        except Exception as e:
            print e

        return column_dict


    def flatten(self, parent_name, data, odict={}):
        # if list, flatten the list
        if isinstance(data, list):
            for value in data:
                self.flatten(parent_name, value, odict)
        # if dictionary, flatten the dictionary
        elif isinstance(data, dict):
            for (key, value) in data.items():
                # if no dict or list, add to odict
                if not isinstance(value, (dict, list)):
                    if parent_name:
                        key = parent_name + "_" + key
                    odict[key] = value
                else:
                    self.flatten(key, value, odict)