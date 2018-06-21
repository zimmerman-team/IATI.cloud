from OIPA.production_settings import *  # noqa: F401, F403

# See:https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/spatialite/
# FIXME: this is currently tested with for Mac OS X and the path is hardcoded:
SPATIALITE_LIBRARY_PATH = '/usr/local/lib/mod_spatialite.dylib'

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
