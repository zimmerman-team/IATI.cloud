import json
import models
import httplib
import urllib2
import sys

class DatasetSyncer():

    def synchronize_with_iati_api(self, type):
        if type == 1:
            cur_url = "http://www.iatiregistry.org/api/search/dataset?filetype=activity&all_fields=1&limit=1000&offset="

        if type == 2:
            cur_url = "http://www.iatiregistry.org/api/search/dataset?filetype=organisation&all_fields=1&limit=1000&offset="

        for i in range(0, 10000, 200):
            cur_url_with_offset = cur_url + str(i)
            self.synchronize_with_iati_api_by_page(cur_url_with_offset, type)

    def synchronize_with_iati_api_by_page(self,cur_url, cur_type, try_number = 0):
        try:

            req = urllib2.Request(cur_url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json_objects = json.load(f)

            if not (json_objects is None):
    #            For each json object
                for object in json_objects["results"]:

                    try:

        #               If download url is not already in OIPA
                        if not (models.iati_xml_source.objects.filter(source_url=object["download_url"]).count() > 0):


                            print "starting on: " + object["download_url"] + ", cur url = " + cur_url

                            publisher_iati_id = None
                            if "publisher_iati_id" in object["extras"]:
                                publisher_iati_id = object["extras"]["publisher_iati_id"]

                            #                   If publisher_iati_id is given
                            if not (publisher_iati_id is None) and not (publisher_iati_id == ""):
        #                        and is already in the database, get the publisher_id, else add the publisher
                                if(models.Publisher.objects.filter(org_abbreviate=publisher_iati_id).count() > 0):
                                    current_publisher = models.Publisher.objects.get(org_abbreviate=publisher_iati_id)
                                else:
                                    current_publisher = self.add_publisher_to_db(publisher_iati_id,publisher_iati_id)
                            else:
                                if(models.Publisher.objects.filter(org_abbreviate=publisher_iati_id).count() > 0):
                                    current_publisher = models.Publisher.objects.filter(org_abbreviate=publisher_iati_id)[0]
                                else:
                                    current_publisher = self.add_publisher_to_db("Unknown","Unknown")
        #                        publisher unknown


                            current_source = self.add_iati_xml_source_to_db(object, current_publisher, cur_type)
                            # self.add_source_to_parse_schedule(object, current_source)

                    except:
                        print "Unexpected error:", sys.exc_info()[0]


        except urllib2.HTTPError, e:
            print 'HTTP error: ' + str(e.code) + " " + cur_url
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            print 'URL error: ' + str(e.reason)
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)
        except httplib.HTTPException, e:
            print 'HTTP exception'
            if try_number < 6:
                self.synchronize_with_iati_api_by_page(cur_url, cur_type,try_number + 1)


    def add_publisher_to_db(self, org_name_value, org_abbreviate_value):
        new_publisher = models.Publisher(org_name=org_name_value, org_abbreviate=org_abbreviate_value, default_interval='MONTHLY')
        new_publisher.save()
        return new_publisher

    def add_iati_xml_source_to_db(self, object, current_publisher, cur_type):
        name = object["name"]
        url = str(object["download_url"])
        url = url.replace(" ", "%20")

        new_source = models.iati_xml_source(ref=name, publisher=current_publisher, source_url=url, type=cur_type)
        new_source.save()
        return new_source

    # def add_source_to_parse_schedule(self, object, current_source):
    #     new_schedule = models.ParseSchedule(iati_xml_source=current_source, interval="MONTHLY")
    #     new_schedule.save()
    #     return new_schedule
    #
