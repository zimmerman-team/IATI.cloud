from settings import *

SECRET_KEY = 'j!bxt0h-=d)1@2r8du!+e4m9x-y*5od7+zq&=tfjwq(ecuov!*'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'oipa_test', # <- change with database name
        'USER': 'root', # <- change with db user
	'HOST': '127.0.0.1',
        'OPTIONS': { 'init_command': 'SET storage_engine=INNODB;' }
    }
}

#DATABASES = {'default': {
#        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
#        'NAME': ':memory:',
#    }
#}