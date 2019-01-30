from OIPA.development_settings import *  # NOQA: F403

DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'  # NOQA: F405 E501
DATABASES['default']['HOST'] = 'db'  # NOQA: F405
