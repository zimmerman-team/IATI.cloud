import json
import models
import httplib
import urllib2
import datetime
from iati.models import OrganisationIdentifier
from iati_synchroniser.exception_handler import exception_handler

class DatasetSyncer():


    # Start looping through the datasets
    def synchronize_with_iati_api(self, type):
        if type == 1:
            cur_url = "http://www.iatiregistry.org/api/search/dataset?extras_filetype=activity&all_fields=1&limit=200&offset="

        if type == 2:
            cur_url = "http://www.iatiregistry.org/api/search/dataset?extras_filetype=organisation&all_fields=1&limit=200&offset="

        for i in range(0, 10000, 200):
            cur_url = cur_url.strip().replace(" ", "%20")
            cur_url_with_offset = cur_url + str(i)
            self.synchronize_with_iati_api_by_page(cur_url_with_offset, type)

    # Loop through the datasets by page
    def synchronize_with_iati_api_by_page(self, cur_url, cur_type, try_number = 0):
        try:

            req = urllib2.Request(cur_url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json_objects = json.load(f)

            if not (json_objects is None):

                #   For each dataset object
                for object in json_objects["results"]:

                    try:

                        publisher_iati_id = None
                        publisher_abbreviation = ""
                        publisher_name = "Unknown"
                        source_url = str(object["res_url"][0])
                        source_url = source_url.replace(" ", "%20")
                        source_name = object["name"]
                        source_title = ""
                        if "title" in object:
                            source_title = object["title"]


                        if "publisher_iati_id" in object["extras"]:
                            publisher_iati_id = object["extras"]["publisher_iati_id"]

                        if "data_dict" in object:
                            try:
                                data_dict = json.loads(object["data_dict"])
                                if "organization" in data_dict and data_dict["organization"]:
                                    if "title" in data_dict["organization"]:
                                        publisher_name = data_dict["organization"]["title"]
                            except Exception as e:
                                exception_handler(e, "synchronize_with_iati_api_by_page", "Unexpected error in synchronize_with_iati_api_by_page organisation match:")


                        #   If download url is not already in OIPA
                        if not models.IatiXmlSource.objects.filter(source_url=source_url).exists():

                            #   If publisher_iati_id is given
                            if publisher_iati_id and (publisher_iati_id != ""):

                                current_publisher = self.update_publisher(publisher_iati_id, publisher_abbreviation, publisher_name)
                            else:

                                # else publisher is unknown
                                current_publisher = self.add_publisher_to_db("Unknown", "Unknown", "Unknown")


                            self.add_iati_xml_source_to_db(source_url, source_title, source_name, current_publisher, cur_type)

                        else:
                            exception_handler(None, "Updated publisher and last found in registry on: ", source_url)

                            cursource = models.IatiXmlSource.objects.get(source_url=source_url)
                            cursource.last_found_in_registry = datetime.datetime.now()
                            current_publisher = cursource.publisher
                            #check if publisher meta is already known, if not, add it and check if the known publisher already existed and add it to the source
                            if (cursource.publisher.org_id != publisher_iati_id):
                                new_current_publisher = self.update_publisher(publisher_iati_id, publisher_abbreviation, publisher_name)
                                cursource.publisher = new_current_publisher
                            cursource.save(process=False, added_manually=False)

                    except Exception as e:
                        exception_handler(e, "synchronize_with_iati_api_by_page", "Unexpected error")



        except urllib2.HTTPError, e:
            exception_handler(e, "HTTP error", cur_url)
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            exception_handler(e, "URL error", cur_url)
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)
        except httplib.HTTPException, e:
            exception_handler(e, "HTTP Exception", cur_url)
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)


    def update_publisher(self, publisher_iati_id, publisher_abbreviation, publisher_name):

        try:
            #   if already in the database, get the publisher_id, else add the publisher
            if (models.Publisher.objects.filter(org_id=publisher_iati_id).exists()):
                current_publisher = models.Publisher.objects.get(org_id=publisher_iati_id)
            else:
                # get the abbreviation from organisation_identifier table
                if(OrganisationIdentifier.objects.filter(code=publisher_iati_id).exists()):
                    current_publisher_meta = OrganisationIdentifier.objects.get(code=publisher_iati_id)
                    publisher_abbreviation = current_publisher_meta.abbreviation

                current_publisher = self.add_publisher_to_db(publisher_iati_id, publisher_abbreviation, publisher_name)

            return current_publisher

        except Exception as e:
            exception_handler(e, publisher_iati_id, "dataset_syncer.update_publisher")

    def add_publisher_to_db(self, org_id, org_abbreviate_value, org_name_value):
        new_publisher = models.Publisher(org_id=org_id, org_abbreviate=org_abbreviate_value, org_name=org_name_value, default_interval='MONTHLY')
        new_publisher.save()
        return new_publisher

    def add_iati_xml_source_to_db(self, url, title, name, current_publisher, cur_type):
        new_source = models.IatiXmlSource(ref=name, title=title, publisher=current_publisher, source_url=url, type=cur_type)
        new_source.save(process=False, added_manually=False)
        return new_source
