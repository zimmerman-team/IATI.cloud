from OIPA.development_settings import *  # NOQA: F403

DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'  # NOQA: F405 E501
DATABASES['default']['HOST'] = 'db'  # NOQA: F405

REDIS_URL = 'redis://oipa-redis:6379/0'

RQ_REDIS_URL = REDIS_URL
RQ_QUEUES['default']['URL'] = REDIS_URL  # NOQA: F405
RQ_QUEUES['parser']['URL'] = REDIS_URL  # NOQA: F405
RQ_QUEUES['export']['URL'] = REDIS_URL  # NOQA: F405
RQ_QUEUES['document_collector']['URL'] = REDIS_URL  # NOQA: F405

CACHES['default']['LOCATION'] = REDIS_URL  # NOQA: F405
CACHES['api']['LOCATION'] = REDIS_URL  # NOQA: F405
