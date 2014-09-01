from cache.models import *
import urllib2
import httplib
from django.conf import settings
import json
from contexttimer import Timer
import datetime


class Validator():

    start_caching_from = 0.6 # seconds in query time

    def is_cached(self, call):

        if call.__len__() < 255:

            # check if call is in requested_calls table
            if RequestedCall.objects.filter(call=call).exists():
                the_call = RequestedCall.objects.get(call=call)
                the_call.count = the_call.count + 1
                the_call.save()
                if the_call.cached:
                    if CachedCall.objects.filter(call=call).exists():
                        return True
            else:
                if not "flush" in call:
                    the_call = RequestedCall(call=call, cached=False, response_time=None, count=1)
                    the_call.save()
            return False
        else:
            return False

    def update_response_times_and_add_to_cache(self):

        for entry in RequestedCall.objects.filter(response_time=None):

            data = None
            #perform the code with a timer
            try:
                with Timer() as t:
                    data = self.perform_api_call(entry.call)
                time_elapsed = t.elapsed
            finally:
                if data:
                    #if t in seconds > min query time to cache, store the call
                    if time_elapsed > self.start_caching_from:

                        the_api_cache = CachedCall(call=entry.call, result=data, last_fetched=datetime.datetime.now())
                        the_api_cache.save()
                        entry.cached = True
                    entry.response_time = time_elapsed
                    entry.save()


    def cache_all_requests(self):

        for entry in RequestedCall.objects.all():
            data = self.perform_api_call(entry.call)
            if data:
                the_api_cache = CachedCall(call=entry.call, result=data, last_fetched=datetime.datetime.now())
                the_api_cache.save()
                entry.cached = True
                entry.save()


    def perform_api_call(self, call):


        site = settings.SITE_URL
        fullurl = site + call

        if ("?" in fullurl):
            fullurl += "&flush=true"
        else:
            fullurl += "?flush=true"

        try:
            req = urllib2.Request(fullurl)
            opener = urllib2.build_opener()
            data = opener.open(req)
            if "json" in fullurl:
                json_objects = json.load(data)
                json_string = json.dumps(json_objects)
                return json_string
            else:
                #xml call, TO DO
                return None

        except urllib2.HTTPError, e:
            print 'HTTP error: ' + str(e.code)

        except urllib2.URLError, e:
            print 'URL error: ' + str(e.reason)

        except httplib.HTTPException, e:
            print 'HTTP exception' + str(e.code)

        return None

    def update_cache_calls(self):
        for entry in CachedCall.objects.all():

            try:

                data = self.perform_api_call(entry.call)
                if data:
                    entry.result = data
                    entry.last_fetched=datetime.datetime.now()
                    entry.save()

            except Exception as e:
                print e.message

    def get_cached_call(self, call):
        data = CachedCall.objects.get(call=call).result
        return data


    def delete_all_under_x(self, number):
        try:

            for entry in RequestedCall.objects.filter(count__lt=number):
                if CachedCall.objects.filter(call=entry.call).exists():
                    CachedCall.objects.get(call=entry.call).delete()
                entry.delete()
            return True

        except Exception as e:
            print type(e)
            print e.message
            return False