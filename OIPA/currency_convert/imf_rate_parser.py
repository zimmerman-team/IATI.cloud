from calendar import monthrange
import datetime
import mechanize
import cookielib
from lxml import etree
from decimal import Decimal
from decimal import InvalidOperation
from currency_convert.models import MonthlyAverage
from iati_codelists.models import Currency


class RateBrowser():
    #
    # def __init__(self):
    #     self.browser = self.prepare_browser()

    def prepare_browser(self):
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
        browser.set_debug_redirects(False)
        browser.set_debug_responses(False)

        # User-Agent
        browser.addheaders = [
            (
                'User-agent',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
            )]

        return browser

    def get_xml_data(self, url, download_url):
        browser = self.prepare_browser()
        browser.open(url, timeout=80)
        response = browser.open(download_url, timeout=80)
        xml_data = response.read()
        browser.close()
        return etree.fromstring(str(xml_data))


class RateParser():

    def __init__(self):
        self.imf_url = "http://www.imf.org/external/np/fin/ert/GUI/Pages/Report.aspx?Type=XML&CU=%27EUR%27,%27JPY%27,%27GBP%27,%27USD%27,%27DZD%27,%27AUD%27,%27ATS%27,%27BHD%27,%27BEF%27,%27VEF%27,%27BWP%27,%27BRL%27,%27BND%27,%27CAD%27,%27CLP%27,%27CNY%27,%27COP%27,%27CYP%27,%27CZK%27,%27DKK%27,%27DEM%27,%27FIM%27,%27FRF%27,%27GRD%27,%27HUF%27,%27ISK%27,%27INR%27,%27IDR%27,%27IRR%27,%27IEP%27,%27ILS%27,%27ITL%27,%27KZT%27,%27KRW%27,%27EEK%27,%27KWD%27,%27LYD%27,%27LUF%27,%27MYR%27,%27MTL%27,%27MUR%27,%27MXN%27,%27NPR%27,%27NLG%27,%27NZD%27,%27NOK%27,%27PEN%27,%27PKR%27,%27UYU%27,%27PHP%27,%27PLN%27,%27PTE%27,%27QAR%27,%27OMR%27,%27RUB%27,%27SAR%27,%27SGD%27,%27SKK%27,%27SIT%27,%27ZAR%27,%27ESP%27,%27LKR%27,%27SEK%27,%27CHF%27,%27THB%27,%27TTD%27,%27TND%27,%27AED%27,%27VEB%27&EX=SDRC&P=DateRange&CF=UnCompressed&CUF=Period&DS=Ascending&DT=NA"
        self.imf_download_url = "http://www.imf.org/external/np/fin/ert/GUI/Pages/ReportData.aspx?Type=XML"
        self.year = 1993
        self.month = 12
        self.min_tick = 0
        self.max_tick = 0
        self.now = datetime.datetime.now()
        self.browser = RateBrowser()
        self.rates = {}

    def prepare_url(self):
        """
        builds the url to get imf data by month.
        tickrates is what imf uses for dates, some timestamp kind of thing.

        min_tick = start of month tick
        max_tick = end of month tick
        """
        return ''.join([
            self.imf_url,
            '&Fr=',
            str(self.min_tick),
            '&To=',
            str(self.max_tick)])

    def parse_day_rates(self, effective_rate_elem):
        for rate_value in effective_rate_elem.getchildren():

            currency = rate_value.attrib.get('ISO_CHAR_CODE', '')
            currency_name = rate_value.attrib.get('CURRENCY_CODE', '')

            try:
                value = Decimal(rate_value.text)
            except InvalidOperation:
                continue

            if currency not in self.rates:
                self.rates[currency] = {
                    'name': currency_name,
                    'values': []
                }

            self.rates[currency]['values'].append(value)

    def parse_data(self, data):
        """
        receives exchange rates per day for 1 specific month in xml format.

        should calculate averages per currency for all dates that an exchange rate is available.
        """
        for e in data.getchildren():
            if e.tag == 'ReportName':
                print e.text
            if e.tag == 'EFFECTIVE_DATE':
                self.parse_day_rates(e)

        self.save_averages()

    def save_averages(self):

        for currency_iso, cur_obj in self.rates.iteritems():
            average_value = sum(cur_obj['values'])/len(cur_obj['values'])

            currency, created = Currency.objects.get_or_create(
                code=currency_iso,
                defaults={'name': cur_obj['name']})

            obj, created = MonthlyAverage.objects.get_or_create(
                month=self.month,
                year=self.year,
                currency=currency,
                defaults={'value': average_value})

            if not created:
                obj.value = average_value
                obj.save()

    def ticks(self, dt):
        return long((dt - datetime.datetime(1, 1, 1)).total_seconds() * 10000000)

    def set_tick_rates(self):
        """
        get first and last day of the month and set tickrates
        """

        # returns tuple of weekday of first day of the month and number of days in month
        month_range = monthrange(self.year, self.month)
        last_day_of_month = month_range[1]

        self.min_tick = self.ticks(datetime.datetime(self.year, self.month, 1))
        self.max_tick = self.ticks(datetime.datetime(self.year, self.month, last_day_of_month))

    def reset_data(self):
        self.rates = {}

    def update_rates(self, force):
        """


        force: re-parse rates even when there's already data in the db for this year / month combination.
        """
        while self.year < self.now.year or self.month < self.now.month:
            if self.month == 12:
                self.year += 1
                self.month = 1
            else:
                self.month += 1

            if not force and MonthlyAverage.objects.filter(year=self.year, month=self.month).count():
                continue

            self.set_tick_rates()
            url = self.prepare_url()
            data = self.browser.get_xml_data(url, self.imf_download_url)
            self.parse_data(data)
            # reset data for next loop
            self.reset_data()
