# Sample production settings, change as needed

from OIPA.base_settings import *

DEBUG = True
FTS = True

MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS += {
    'debug_toolbar',
}

def custom_show_toolbar(self):
    return True

SECRET_KEY = '__DEV_SECRET_KEY__'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'oipa',
        'USER': 'oipa',
        'PASSWORD': 'oipa',
        'HOST': '127.0.0.1',
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, 'static_served/')

# Additional locations of static files
STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static/'),
)

FIXTURE_DIRS = (
     os.path.join(BASE_DIR, '../fixtures/'),
)

CKAN_URL = "https://iati-staging.ckan.io"

try:
    from local_settings import *
except ImportError:
    pass
