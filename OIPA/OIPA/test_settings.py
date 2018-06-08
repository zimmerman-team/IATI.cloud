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
