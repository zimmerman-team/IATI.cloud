import urllib2
import httplib
import logging
import mechanize
import cookielib

logger = logging.getLogger(__name__)


class FileGrabber():
    def __init__(self):
        """
        Get the file of an URL, use mechanize / cookiejar to simulate a browser because some IATI XML URLs deny bots
        """
        browser = mechanize.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        browser.set_cookiejar(cj)

        # Browser options
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        browser.set_debug_http(False)
        browser.set_debug_redirects(True)
        browser.set_debug_responses(True)

        # User-Agent
        browser.addheaders = [
            (
                'User-agent',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
            )]

        self.browser = browser

    def get_the_file(self, url, try_number=0):
        try:
            response = self.browser.open(url, timeout=10)
            self.browser.close()
            return response

        except urllib2.HTTPError, e:
            logger.info('HTTPError (url=' + url + ') = ' + str(e.code))
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
            else:
                return None
        except urllib2.URLError, e:
            logger.info('URLError (url=' + url + ') = ' + str(e.reason))
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
        except httplib.HTTPException, e:
            logger.info('HTTPException reading url ' + url)
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
        except Exception as e:
            logger.info('%s (%s)' % (e.message, type(e)) + " in get_the_file: " + url)
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)

