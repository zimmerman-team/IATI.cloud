import sys
sys.path.append('../OIPA')

import os, django
os.environ["DJANGO_SETTINGS_MODULE"] = "OIPA.settings"
django.setup()

import time
import datetime
from iati.models import Activity
from iati.transaction.models import Transaction, TransactionProvider, TransactionReceiver
from iati_synchroniser.models import IatiXmlSource
from iati.filegrabber import FileGrabber

import gzip
import tarfile
import StringIO
from random import randint

from email.utils import parsedate

def _parse_http_datetime(s):
        return time.mktime(parsedate(s))


source_count = IatiXmlSource.objects.count()

if source_count is 0:
    print("No IATI sources have been parsed yet.")
    exit(1)

date_now = datetime.date.isoformat(datetime.datetime.now())
directory = 'iati-{}'.format(date_now)

if os.path.exists(directory):
    print("IATI sources already compressed on this date")
    exit(1)

os.makedirs(directory)

def handle_response(tar, source):
        file_grabber = FileGrabber()
        response = file_grabber.get_the_file(source.source_url)
        if not response or response.code != 200:
            print("source url {} down or doesn't exist".format(source.source_url))
            return
        modified_time = response.info().get('Last-Modified')

        iati_file = StringIO.StringIO(response.read())

        info = tarfile.TarInfo(
                name="{}.xml".format(source.ref)
                )

        info.size = len(iati_file.buf)

        if modified_time:
            info.mtime = _parse_http_datetime(modified_time)

        tar.addfile(tarinfo=info, fileobj=iati_file)


activities_path = '{}/iati-activities-{}.tgz'.format(directory, date_now)
organisations_path = '{}/iati-organisations-{}.tgz'.format(directory, date_now)

with tarfile.open(activities_path, 'w:gz') as tar:
    for source in IatiXmlSource.objects.all().filter(type=1):
        handle_response(tar, source)

with tarfile.open(organisations_path, 'w:gz') as tar:
    for source in IatiXmlSource.objects.all().filter(type=2):
        handle_response(tar, source)

print("Done, compressed {} IATI source files".format(source_count))

