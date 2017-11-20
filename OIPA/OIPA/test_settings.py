from OIPA.production_settings import *  # noqa: F401, F403

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': ':memory:',
    },
}

FTS_ENABLED = False
CKAN_URL = "https://iati-staging.ckan.io"
