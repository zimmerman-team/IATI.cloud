# Sample production settings, change as needed

DEBUG = False

# for signing keys: https://docs.djangoproject.com/en/1.8/topics/signing/
SECRET_KEY = '__SECRET_KEY_HERE__'

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

STATIC_ROOT = os.path.join(BASE_DIR, "static")

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
