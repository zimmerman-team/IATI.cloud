# Sample production settings, change as required

from OIPA.base_settings import *

BASE_DIR = os.path.dirname(os.path.realpath(__name__))

DEBUG = False

# for signing keys: https://docs.djangoproject.com/en/1.8/topics/signing/
SECRET_KEY = '__SECRET_KEY_HERE__'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'oipa',
        'USER': 'oipa',
        'PASSWORD': 'oipa',
        'HOST': '127.0.0.1',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    }
}

API_CACHE_SECONDS = 60 * 60 * 24

ROOT_ORGANISATIONS = []

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static/'),
)

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'parser': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    }
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'OIPA.wsgi.application'

try:
    from local_settings import *
except ImportError:
    pass

