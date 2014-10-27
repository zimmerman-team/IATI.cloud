import os

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

STATIC_ROOT = rel('../static-root')
STATIC_URL = '/static/'

ADMINS = (
     # ('pp', 'vincent@zimmermanzimmerman.nl'),
)

SITE_URL = 'http://dev.oipa.openaidsearch.org'

SERVER_EMAIL = ''

MANAGERS = ADMINS

SECRET_KEY = "4g*t76mgdhna-=fdqx0@ek8=*c(cdj0djitnw10g5kvv6brc9d"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'oipa', # <- change with database name
        'USER': 'travis', # <- change with db user
        'PASSWORD': 'travis',
        'HOST': '/var/run/mysqld/mysqld.sock',
        'PORT': '3306',
        'OPTIONS': { 'init_command': 'SET storage_engine=INNODB;' }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/robin/log/oipa/debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
    'high': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379'), # If you're on Heroku
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    }
}
