# Django settings for OIPA project.
import sys
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.core.urlresolvers import reverse_lazy

BASE_DIR = os.path.dirname(os.path.realpath(__name__))

LOGIN_URL = reverse_lazy('two_factor:login')

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

sys.path.insert(0, rel('..','lib'))

ADMINFILES_UPLOAD_TO = 'csv_files'

XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['GET', 'OPTIONS']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
XS_SHARING_ALLOWED_CREDENTIALS = 'true'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
MEDIA_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static/'),
)

# URL for static files
STATIC_URL = "/static/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'OIPA.urls'

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

# TODO: clean this up, separate into test_settings, etc..
INSTALLED_APPS = (
    'django_rq',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
    'corsheaders',
    'haystack',
    'iati',
    'organisation',
    'iati_synchroniser',
    'geodata',
    'indicator',
    'api',
    'task_queue',
    'multiupload',
    'djsupervisor',
    'indicator_unesco',
    'translation_model',
    'rest_framework',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'otp_yubikey',
    'two_factor',
    'debug_toolbar',
    'parse_logger',
    'django_extensions',
    'iati_vocabulary',
    'iati_codelists',
    'test_without_migrations',
    'nested_inline',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'OIPA',
    'MENU': (
        # Keep original label and models
        'sites',
        # Rename app and set icon
        {'label': 'Authorization', 'icon':'icon-lock', 'models': (
            'auth.user',
            'auth.group',
            {'label': 'Two Factor Authentication settings', 'url': '/account/two_factor/'},
            {'label': 'OTP Static devices', 'model': 'otp_static.staticdevice'},
            {'label': 'OTP TOTP devices', 'model': 'otp_totp.totpdevice'},
            {'label': 'Two factor phone devices', 'model': 'two_factor.phonedevice'},
            {'label': 'Local YubiKey devices', 'model': 'otp_yubikey.yubikeydevice'},
            {'label': 'Remote YubiKey devices', 'model': 'otp_yubikey.remoteyubikeydevice'},
            {'label': 'YubiKey validation services', 'model': 'otp_yubikey.validationservice'},
        )},
        {'app': 'iati', 'label': 'IATI', 'icon': 'icon-th'},
        {'app': 'iati_codelists', 'label': 'IATI codelist', 'icon': 'icon-barcode'},
        {'app': 'iati_synchroniser', 'label': 'IATI management', 'icon': 'icon-refresh'},
        {'app': 'geodata', 'label': 'Geo data', 'icon': 'icon-globe'},
        {'app': 'indicator', 'label': 'Indicators', 'icon': 'icon-signal'},
        {'app': 'indicator_unesco', 'label': 'Unesco Indicators', 'icon': 'icon-signal'},
        {'app': 'cache', 'label': 'API call cache', 'icon': 'icon-hdd'},
        {'label': 'Task queue', 'url': '/admin/queue/', 'icon': 'icon-tasks', 'models': [
            {'label': 'Task overview', 'url': '/admin/queue/'},
            {'label': 'Default queue', 'url': '/admin/queue/queues/0/'},
            {'label': 'Parse queue', 'url': '/admin/queue/queues/1/'},
            {'label': 'Failed tasks', 'url': '/admin/queue/queues/2/'},
        ]},
        {'app': 'parse_logger', 'label': 'Parse Log', 'icon': 'icon-hdd'},
    )
}

RQ_SHOW_ADMIN_LINK = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 400,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        # 'rest_framework.filters.SearchFilter',
    )
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_METHODS = ('GET',)

ROOT_ORGANISATIONS = []

