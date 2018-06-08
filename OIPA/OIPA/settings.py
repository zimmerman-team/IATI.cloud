# Django settings for OIPA project.

import os
import sys
from ast import literal_eval
from os import environ as env

from django.urls import reverse_lazy
from tzlocal import get_localzone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEBUG = literal_eval(env.get('OIPA_DEBUG', 'True'))
FTS_ENABLED = literal_eval(env.get('OIPA_FTS_ENABLED', 'True'))

LOGIN_URL = reverse_lazy('two_factor:login')
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_URL = '/logout'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

SECRET_KEY = env.get('OIPA_SECRET_KEY', 'PXwlMOpfNJTgIdQeH5zk39jKfUMZPOUK')

DATABASES = {
    'default': {
        'ENGINE': env.get(
            'OIPA_DB_ENGINE', 'django.contrib.gis.db.backends.postgis'
        ),
        'HOST': env.get('OIPA_DB_HOST', 'localhost'),
        'PORT': env.get('OIPA_DB_PORT', '5432'),
        'NAME': env.get('OIPA_DB_NAME', 'oipa'),
        'USER': env.get('OIPA_DB_USER', 'oipa'),
        'PASSWORD': env.get('OIPA_DB_PASSWORD', 'oipa'),
        'CONN_MAX_AGE': int(env.get('OIPA_DB_CONN_MAX_AGE', 500))
    },
}

# For testing with spatialite
SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #    ('django.template.loaders.cached.Loader', [
            #        'django.template.loaders.filesystem.Loader',
            #        'django.template.loaders.app_directories.Loader',
            #    ]),
            # ],
        },
    },
]


def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)


sys.path.insert(0, rel('..', 'lib'))

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.get('OIPA_ALLOWED_HOSTS', '*').split()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.


TIME_ZONE = get_localzone().zone

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

APPEND_SLASH = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# URL for static files
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get(
    'OIPA_STATIC_ROOT',
    os.path.join(
        os.path.dirname(BASE_DIR),
        'public/static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get(
    'OIPA_MEDIA_ROOT',
    os.path.join(
        os.path.dirname(BASE_DIR),
        'public/media'))

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'OIPA.wsgi.application'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'OIPA.urls'

INSTALLED_APPS = [
    'django_rq',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'grappelli',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
    'corsheaders',
    'common',
    'iati.apps.IatiConfig',
    'iati_organisation.apps.IatiOrganisationConfig',
    'iati_synchroniser.apps.IatiSynchroniserConfig',
    'geodata.apps.GeodataConfig',
    'currency_convert.apps.CurrencyConvertConfig',
    'traceability.apps.TraceabilityConfig',
    'api',
    'task_queue',
    'djsupervisor',
    'rest_framework',
    'rest_framework_csv',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'otp_yubikey',
    'two_factor',
    'django_extensions',
    'iati_vocabulary.apps.IatiVocabularyConfig',
    'iati_codelists.apps.IatiCodelistsConfig',
    'test_without_migrations',
    'admin_reorder',
    'rest_framework.authtoken',
    'iati.permissions',
    'rest_auth',
    'rest_auth.registration',
    'django_filters'
]

ADMIN_REORDER = (
    'iati',
    'iati_synchroniser',
    'iati_codelists',
    'iati_vocabulary',
    'iati_organisation',
    'geodata',
    'currency_convert',
    'auth',
    'sites'
)

RQ_SHOW_ADMIN_LINK = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
        'api.renderers.PaginatedCSVRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

RQ_REDIS_URL = env.get('OIPA_RQ_REDIS_URL', 'redis://localhost:6379/0')

RQ_QUEUES = {
    'default': {
        'URL': RQ_REDIS_URL,
        'DEFAULT_TIMEOUT': 3600,
    },
    'parser': {
        'URL': RQ_REDIS_URL,
        'DEFAULT_TIMEOUT': 5400,
    },
    'export': {
        'URL': RQ_REDIS_URL,
        'DEFAULT_TIMEOUT': 5400,
    },
    'document_collector': {
        'URL': RQ_REDIS_URL,
        'DEFAULT_TIMEOUT': 5400,
    }
}

GRAPPELLI_ADMIN_TITLE = 'OIPA admin'
ADMINFILES_UPLOAD_TO = 'csv_files'

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_METHODS = ('GET',)

IATI_PARSER_DISABLED = False
CONVERT_CURRENCIES = True
ROOT_ORGANISATIONS = []

ERROR_LOGS_ENABLED = literal_eval(env.get('OIPA_ERROR_LOGS_ENABLED', 'True'))

DEFAULT_LANG = 'en'
# django-all-auth
ACCOUNT_EMAIL_VERIFICATION = 'none'

# django-rest-auth
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'api.permissions.serializers.UserSerializer',
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'api.permissions.serializers.RegistrationSerializer'
}

EXPORT_COMMENT = 'Published using the IATI Studio publisher'

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, '../fixtures/'),
)

CKAN_URL = env.get('OIPA_CKAN_URL', 'https://iati-staging.ckan.io')

API_CACHE_SECONDS = int(env.get('OIPA_API_CACHE_SECONDS', 0))

CACHES = {
    'default': {
        'BACKEND': env.get(
            'OIPA_CACHES_DEFAULT_BACKEND', 'redis_cache.RedisCache'
        ),
        'LOCATION': env.get('OIPA_CACHES_DEFAULT_LOCATION', 'localhost:6379'),
    },
    'api': {
        'BACKEND': env.get(
            'OIPA_CACHES_DEFAULT_BACKEND', 'redis_cache.RedisCache'
        ),
        'LOCATION': env.get('OIPA_CACHES_DEFAULT_LOCATION', 'localhost:6379'),
    }
}

OIPA_LOG_LEVEL = env.get('OIPA_LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'  # NOQA: E501
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': OIPA_LOG_LEVEL,
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': OIPA_LOG_LEVEL
        },

        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': OIPA_LOG_LEVEL
        }
    }
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_USE_CACHE': 'api',
    # reset cache every x seconds:
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 1 * 60 * 60 * 24 * 7,  # 1 week
}

try:
    from local_settings import *  # noqa: F401, F403
except ImportError:
    pass
