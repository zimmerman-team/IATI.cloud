import os
from datetime import datetime

from OIPA.production_settings import *  # noqa: F401, F403

# XXX: Note, that for OS X you'll probably need something different, something
# like '/usr/local/lib/mod_spatialite.dylib' or smth.
# See:https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/spatialite/
SPATIALITE_LIBRARY_PATH = os.getenv(
    'SPATIALITE_LIBRARY_PATH',
    'mod_spatialite',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': ':memory:',
    },
}

FTS_ENABLED = False
CKAN_URL = "https://iati-staging.ckan.io"

# Don't cache anything when testing:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'api': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

# Log everything to console when testing:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # Useful for local development:
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # All other errors:
        '': {
            'handlers': ['console'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
        # IATI Parser related errors:
        'iati.parser': {
            'handlers': ['console'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
        # Django-related errors:
        'django': {
            'handlers': ['console'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
    },
}

# UNESCO specific for calculated transaction by year period
PERIOD_YEAR = datetime.now().year
