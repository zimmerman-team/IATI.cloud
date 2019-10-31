from OIPA.production_settings import *  # noqa: F401, F403

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

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'circle_test',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'USERNAME': 'circleci',
        'PASSWORD': ''
    }
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

SOLR = {
    'indexing': False,
    'url': 'http://localhost:8983/solr',
    'cores': {
        'activity': 'activity',
        'budget': 'budget',
        'codelist': {
            'country': 'codelist-country',
            'region': 'codelist-region'
        },
        'dataset': 'dataset',
        'datasetnote': 'datasetnote',
        'organisation': 'organisation',
        'publisher': 'publisher',
        'result': 'result',
        'transaction': 'transaction'
    }
}
