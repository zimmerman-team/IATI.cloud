"""Downloads files from http or ftp locations.

Copyright Joshua Banton"""
import ftplib
import hashlib
import os
import socket
import urllib
from time import sleep, time
from urllib import parse, request


class DownloadFile(object):
    """This class is used for downloading files from the internet via http or
    ftp.
    It supports basic http authentication and ftp accounts, and supports
    resuming downloads.
    It does not support https or sftp at this time.

    The main advantage of this class is it's ease of use, and pure pythoness.
    It only uses the Python standard library,
    so no dependencies to deal with, and no C to compile.

    #####
    If a non-standard port is needed just include it in the url
    (http://example.com:7632).

    #Rate Limiting:
        rate_limit = the average download rate in Bps
        rate_burst = the largest allowable burst in bytes

    Basic usage:
        Simple
            downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.download()
         Use full path to download
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip")
             downloader.download()
         Basic Authentication protected download
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip", ('username','password'))
             downloader.download()
         Resume
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.resume()
    """  # NOQA: E501

    def __init__(
            self,
            url=None,
            localFileName=None,
            auth=None,
            timeout=120.0,
            autoretry=False,
            retries=5,
            fast_start=False,
            aws_key=None,
            aws_secret_key=None,
            aws_bucket_name=None,
            aws_file_key=None,
            rate_limit_on=False,
            rate_limit=500,
            rate_burst=1000):
        """Note that auth argument expects a tuple, ('username','password')."""
        self.url = url
        self.urlFileName = None
        self.progress = 0
        self.fileSize = None
        self.localFileName = localFileName
        if aws_key:
            self.type = 's3'
        else:
            self.type = self.getType()
        self.auth = auth
        self.timeout = timeout
        self.retries = retries
        self.fast_start = fast_start
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_bucket_name = aws_bucket_name
        self.aws_file_key = aws_file_key
        self.curretry = 0
        self.cur = 0
        if not self.fast_start:
            try:
                self.urlFilesize = self.getUrlFileSize()
            except request.HTTPError:
                self.urlFilesize = None
        else:
            self.urlFilesize = None
        # if no filename given pulls filename from the url:
        if not self.localFileName:
            self.localFileName = self.getUrlFilename(self.url)
        self.rate_limit_on = rate_limit_on
        self.rate_limit = rate_limit
        self.rate_burst = rate_burst
        if self.rate_limit_on:
            self.bucket = TokenBucket(self.rate_burst, self.rate_limit)

    def __downloadFile__(self, urlObj, fileObj, callBack=None):
        """starts the download loop"""
        if not self.fast_start:
            self.fileSize = self.getUrlFileSize()
        while True:
            if self.rate_limit_on:
                if not self.bucket.spend(8192):
                    sleep(1)
                    continue
            try:
                data = urlObj.read(8192)
            except (socket.timeout, socket.error) as t:
                self.__retry__()
                break
            if not data:
                fileObj.close()
                break
            fileObj.write(data)
            self.cur += 8192
            if callBack:
                callBack(cursize=self.cur)

    def __retry__(self):
        """auto-resumes up to self.retries"""
        if self.retries > self.curretry:
            self.curretry += 1
            if self.getLocalFileSize() != self.urlFilesize:
                self.resume()
        else:
            # print 'retries all used up'
            return False, "Retries Exhausted"

    def __authHttp__(self):
        """handles http basic authentication"""
        passman = request.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, self.url, self.auth[0], self.auth[1])
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        authhandler = request.HTTPBasicAuthHandler(passman)
        # create the AuthHandler
        opener = request.build_opener(authhandler)
        request.install_opener(opener)

    def __authFtp__(self):
        """handles ftp authentication"""
        ftped = request.FTPHandler()
        ftpUrl = self.url.replace('ftp://', '')
        req = request.Request("ftp://%s:%s@%s" %
                              (self.auth[0], self.auth[1], ftpUrl))
        req.timeout = self.timeout
        ftpObj = ftped.ftp_open(req)
        return ftpObj

    def __startHttpPartial__(self, startPos, endPos, callBack=None):
        f = open(self.localFileName, "wb")
        if self.auth:
            self.__authHttp__()
        req = request.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (startPos, endPos)
        urllib2Obj = request.urlopen(req, timeout=self.timeout)
        self.__downloadFile__(urllib2Obj, f, callBack=callBack)

    def __startHttpResume__(self, restart=None, callBack=None):
        """starts to resume HTTP"""
        curSize = self.getLocalFileSize()
        if curSize >= self.urlFilesize:
            return False
        self.cur = curSize
        if restart:
            f = open(self.localFileName, "wb")
        else:
            f = open(self.localFileName, "ab")
        if self.auth:
            self.__authHttp__()
        req = request.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (curSize, self.getUrlFileSize())
        urllib2Obj = request.urlopen(req, timeout=self.timeout)
        self.__downloadFile__(urllib2Obj, f, callBack=callBack)

    def __startFtpResume__(self, restart=None):
        """starts to resume FTP"""
        curSize = self.getLocalFileSize()
        if curSize >= self.urlFilesize:
            return False
        if restart:
            f = open(self.localFileName, "wb")
        else:
            f = open(self.localFileName, "ab")
        ftper = ftplib.FTP(timeout=60)
        parseObj = parse.urlparse(self.url)
        baseUrl = parseObj.hostname
        urlPort = parseObj.port
        bPath = os.path.basename(parseObj.path)
        gPath = parseObj.path.replace(bPath, "")
        unEncgPath = urllib.unquote(gPath)
        fileName = urllib.unquote(os.path.basename(self.url))
        ftper.connect(baseUrl, urlPort)
        ftper.login(self.auth[0], self.auth[1])
        if len(gPath) > 1:
            ftper.cwd(unEncgPath)
        ftper.sendcmd("TYPE I")
        ftper.sendcmd("REST " + str(curSize))
        downCmd = "RETR " + fileName
        ftper.retrbinary(downCmd, f.write)

    def getUrlFilename(self, url):
        """returns filename from url"""
        return urllib.unquote(os.path.basename(url))

    def getUrlFileSize(self):
        """gets filesize of remote file from ftp or http server"""
        if self.type == 'http':
            if self.auth:
                self.__authHttp__()
            urllib2Obj = request.urlopen(self.url, timeout=self.timeout)
            size = urllib2Obj.headers.get('content-length')
            return size

    def getLocalFileSize(self):
        """gets filesize of local file"""
        size = os.stat(self.localFileName).st_size
        return size

    def getType(self):
        """returns protocol of url (ftp or http)"""
        type = parse.urlparse(self.url).scheme
        return type

    def checkExists(self):
        """Checks to see if the file in the url in self.url exists"""
        if self.auth:
            if self.type == 'http':
                self.__authHttp__()
                try:
                    request.urlopen(self.url, timeout=self.timeout)
                except request.HTTPError:
                    return False
                return True
            elif self.type == 'ftp':
                return "not yet supported"
        else:
            request.urlopen(self.url, timeout=self.timeout)
            try:
                request.urlopen(self.url, timeout=self.timeout)
            except request.HTTPError:
                return False
            return True

    def download(self, callBack=None):
        """starts the file download"""
        self.curretry = 0
        self.cur = 0
        f = open(self.localFileName, "wb")
        if self.auth:
            if self.type == 'http':
                self.__authHttp__()
                urllib2Obj = request.urlopen(self.url, timeout=self.timeout)
                self.__downloadFile__(urllib2Obj, f, callBack=callBack)
            elif self.type == 'ftp':
                self.url = self.url.replace('ftp://', '')
                authObj = self.__authFtp__()
                self.__downloadFile__(authObj, f, callBack=callBack)
        else:
            urllib2Obj = request.urlopen(self.url, timeout=self.timeout)
            self.__downloadFile__(urllib2Obj, f, callBack=callBack)
        return True

    def resume(self, callBack=None):
        """attempts to resume file download"""
        type = self.getType()
        if type == 'http':
            self.__startHttpResume__(callBack=callBack)
        elif type == 'ftp':
            self.__startFtpResume__()

    def partialDownload(self, startPos, endPos, callBack=None):
        """downloads a piece of a file, only supports HTTP"""
        if self.type == 'http':
            self.__startHttpPartial__(startPos, endPos, callBack=callBack)
        elif self.type == 'ftp':
            raise FileDownloaderError("Partial download doesn't support ftp.")


class FileDownloaderError(Exception):
    def __init(self, message=''):
        self.message = message


class TokenBucket(object):
    """
    An implementation of the token bucket algorithm.
    Slightly modified from http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/
    """  # NOQA: E501

    def __init__(self, bucket_size, fill_rate):
        """tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled."""
        self.capacity = float(bucket_size)
        self._tokens = float(bucket_size)
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def spend(self, tokens):
        """Spend tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.get_tokens():
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        now = time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
        self.timestamp = now
        return self._tokens


def hash_file(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        chunk = file.read(1024)
        h.update(chunk)
    return h.hexdigest()
