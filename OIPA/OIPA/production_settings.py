# TODO: load settings.py here (for every env.)

import os

from dotenv import find_dotenv, load_dotenv

from OIPA.settings import *  # NOQA: F401, F403

load_dotenv(find_dotenv())

DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'OIPA_DB_ENGINE', 'django.contrib.gis.db.backends.postgis'
        ),
        'HOST': os.getenv('OIPA_DB_HOST', 'localhost'),
        'PORT': os.getenv('OIPA_DB_PORT', 5432),
        'NAME': os.getenv('OIPA_DB_NAME'),
        'USER': os.getenv('OIPA_DB_USER'),
        'PASSWORD': os.getenv('OIPA_DB_PASSWORD'),
        'CONN_MAX_AGE': int(os.getenv('OIPA_DB_CONN_MAX_AGE', 500))
    },
}

# In production env, log everything to JSON files so DataDog can pick it up:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(threadName)s %(name)s %(thread)s %(created)f %(process)s %(processName)s %(relativeCreated)s %(module)s %(funcName)s %(levelno)s %(msecs)s %(pathname)s %(lineno)s %(asctime)s %(message)s %(filename)s %(levelname)s %(special)s %(run)s',  # NOQA: E501
        },
    },
    'handlers': {
        'oipa-json-logfile': {
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/oipa/oipa/oipa-json.log',
            'formatter': 'json',
        },
        'iati-parser-json-logfile': {
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/oipa/oipa/iati-parser-json.log',
            'formatter': 'json',
        },
        'django-json-logfile': {
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/oipa/oipa/django-json.log',
            'formatter': 'json',
        },
    },
    'loggers': {
        # All other errors:
        '': {
            'handlers': ['oipa-json-logfile'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
        # IATI Parser related errors:
        'iati.parser': {
            'handlers': ['iati-parser-json-logfile'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
        # Django-related errors:
        'django': {
            'handlers': ['django-json-logfile'],
            'level': OIPA_LOG_LEVEL,  # NOQA: F405
            'propagate': False,
        },
    },
}

# FIXME: Caching is disabled COMPLETELY for now.
# See: #680
CACHES = {
    'api': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60 * 60 * 24 * 30,
    },
}

# A setting indicating whether to save XML datasets (files) to local machine or
# not:
DOWNLOAD_DATASETS = True

try:
    from .local_settings import *  # noqa: F401, F403
except ImportError:
    pass
