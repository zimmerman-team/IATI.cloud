import logging
from http import cookiejar

import mechanicalsoup
import requests

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
        session = requests.Session()

        # This is Unesco-specific functionality: the server
        # uses proxies for all outside connections, but here we're
        # accessing Unesco data file that is in the same server and
        # if proxies are used (their settings are taken from the
        # environment variable), 503 response is returned. So we need
        # to skip proxies here:
        session.trust_env = False

        response = session.get(url, timeout=10)

        self.browser.close()

        return response
