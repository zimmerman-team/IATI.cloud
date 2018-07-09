from OIPA.settings import *  # noqa: F401, F403

MIDDLEWARE_CLASSES += [  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'yet_another_django_profiler.middleware.ProfilerMiddleware'
]

INSTALLED_APPS += {  # noqa: F405
    'debug_toolbar',
    'yet_another_django_profiler'
}


def custom_show_toolbar(self):
    return True


SECRET_KEY = '__DEV_SECRET_KEY__'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

# Don't cache anything when developing:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'api': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

IATI_STAGING_CHECK = os.environ['IATI_STAGING_CHECK'] if 'IATI_STAGING_CHECK' in os.environ else True
IATI_STAGING_PUBLISHER_ID = os.environ['IATI_STAGING_PUBLISHER_ID'] if 'IATI_STAGING_PUBLISHER_ID' in os.environ else "XM-DAC-47066"
IATI_STAGING_FILE_ID = os.environ['IATI_STAGING_FILE_ID'] if 'IATI_STAGING_FILE_ID' in os.environ else "staging.xml"
IATI_STAGING_PATH = os.environ['IATI_STAGING_PATH'] if 'IATI_STAGING_PATH' in os.environ else "../../../DHT/media/"
IATI_STAGING_ID = os.environ['IATI_STAGING_ID'] if 'IATI_STAGING_ID' in os.environ else "IOM_staging_file"
IATI_STAGING_FILE_URL = os.environ['IATI_STAGING_FILE_URL'] if 'IATI_STAGING_FILE_URL' in os.environ else "http://127.0.0.1:8000/api/datasets/staging_collection.xml"

