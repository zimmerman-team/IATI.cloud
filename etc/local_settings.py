DEBUG = True

SECRET_KEY = '__SECRET_KEY__'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'oipa',
        'USER': 'oipa',
        'PASSWORD': 'oipa',
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB;',
        }
    },
}

STATIC_URL = '/static/'

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'parser': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    }
}
