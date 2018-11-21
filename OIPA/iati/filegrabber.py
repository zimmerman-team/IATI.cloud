import logging
import urllib
from http import cookiejar
from http.client import HTTPException

import mechanicalsoup

logger = logging.getLogger(__name__)


class FileGrabber():
    def __init__(self):
        """
        Get the file of an URL, use mechanicalsoup / cookiejar to simulate a
        browser because some IATI XML URLs deny bots
        """
        browser = mechanicalsoup.Browser()

        # Cookie Jar
        cj = cookiejar.LWPCookieJar()
        browser.set_cookiejar(cj)

        # User-Agent
        browser.addheaders = [
            ('User-agent',
             'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) \
                     Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        self.browser = browser

    def get_the_file(self, url, try_number=0):
        try:
            response = self.browser.get(url, timeout=10)
            self.browser.close()
            return response

        except urllib.error.HTTPError as e:
            logger.info('HTTPError (url=' + url + ') = ' + str(e.code))
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
            else:
                return None
        except urllib.error.URLError as e:
            logger.info('URLError (url=' + url + ') = ' + str(e.reason))
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
        except HTTPException as e:
            logger.info('HTTPException reading url ' + url)
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
        except Exception as e:
            logger.info('%s (%s)' % (e, type(e)) + " in get_the_file: " + url)
            if try_number < 2:
                return self.get_the_file(url, try_number + 1)
