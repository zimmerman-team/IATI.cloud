import os

from OIPA.settings import *  # NOQA: F401, F403

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
