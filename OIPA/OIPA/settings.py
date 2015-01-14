# Django settings for OIPA project.
import sys
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

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
TIME_ZONE = 'America/Chicago'

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

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
MEDIA_ROOT = rel('../media')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
MEDIA_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    rel('../static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '709)+!x8tujusgf**8v0l%t(u65p3haip^&l17k^t(i_r+csqd'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.v3.ajax_allower.XsSharing',
)

ROOT_URLCONF = 'OIPA.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'OIPA.wsgi.application'

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

INSTALLED_APPS = (
    'django_rq',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
    'iati',
    'iati_synchroniser',
    'geodata',
    'indicator',
    'api',
    'cache',
    'task_queue',
    'multiupload',
    'djsupervisor',
    'indicator_unesco',
    'translation_model',
    'rest_framework',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'OIPA',
    'MENU': (
        # Keep original label and models
        'sites',
        # Rename app and set icon
        {'app': 'auth', 'label': 'Authorization', 'icon':'icon-lock'},
        {'app': 'iati', 'label': 'IATI', 'icon':'icon-th'},
        {'app': 'iati_synchroniser', 'label': 'IATI management', 'icon':'icon-refresh'},
        {'app': 'geodata', 'label': 'Geo data', 'icon':'icon-globe'},
        {'app': 'indicator', 'label': 'Indicators', 'icon':'icon-signal'},
        {'app': 'indicator_unesco', 'label': 'Unesco Indicators', 'icon':'icon-signal'},
        {'app': 'cache', 'label': 'API call cache', 'icon':'icon-hdd'},
        {'label': 'Task queue', 'url': ( '/admin/queue/'), 'icon':'icon-tasks', 'models': [
            {'label': 'Task overview', 'url': ( '/admin/queue/')},
            {'label': 'Default queue', 'url': ( '/admin/queue/queues/0/')},
            {'label': 'Parse queue', 'url': ( '/admin/queue/queues/1/')},
            {'label': 'Failed tasks', 'url': ( '/admin/queue/queues/2/')},
        ]},
    )
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

RQ_SHOW_ADMIN_LINK = True
RQ_QUEUES = {}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    )
}

try:
    from local_settings import *
except ImportError:
    pass

