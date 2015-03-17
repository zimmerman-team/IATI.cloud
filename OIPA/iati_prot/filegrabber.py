import urllib2
import httplib
import logging
import mechanize
import cookielib

logger = logging.getLogger(__name__)

class FileGrabber():

    def get_the_file(self, url, try_number = 0):
        try:

            br = mechanize.Browser()

            # Cookie Jar
            cj = cookielib.LWPCookieJar()
            br.set_cookiejar(cj)

            # Browser options
            br.set_handle_equiv(True)
            br.set_handle_redirect(True)
            br.set_handle_referer(True)
            br.set_handle_robots(False)
            br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
            br.set_debug_http(True)
            br.set_debug_redirects(True)
            br.set_debug_responses(True)

            # User-Agent
            br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

            response = br.open(url, timeout=80)
            return response

            # headers = {'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36'}
            # iati_file_url_object = mechanize.Request(url, headers=headers)
            # file_opener = mechanize.build_opener()
            # iati_file = file_opener.open(iati_file_url_object)
            # return iati_file


        except urllib2.HTTPError, e:
            logger.info('HTTPError (url=' + url + ') = ' + str(e.code))
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            logger.info('URLError (url=' + url + ') = ' + str(e.reason))
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except httplib.HTTPException, e:
            logger.info('HTTPException reading url ' + url)
            if try_number < 6:
                self.get_the_file(url, try_number + 1)
        except Exception as e:
            logger.info('%s (%s)' % (e.message, type(e)) + " in get_the_file: " + url)
            if try_number < 6:
                self.get_the_file(url, try_number + 1)