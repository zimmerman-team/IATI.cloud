# Sample production settings, change as required

import os

from OIPA.settings import *  # noqa: F401, F403

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
        'CONN_MAX_AGE': 500
    },
}

API_CACHE_SECONDS = 60 * 60 * 24

ROOT_ORGANISATIONS = []

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'OIPA.wsgi.application'

ERROR_LOGS_ENABLED = False

try:
    from local_settings import *  # noqa: F401, F403
except ImportError:
    pass
