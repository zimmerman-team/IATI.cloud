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
