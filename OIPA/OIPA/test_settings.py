from settings import *

SECRET_KEY = 'j!bxt0h-=d)1@2r8du!+e4m9x-y*5od7+zq&=tfjwq(ecuov!*'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': ':memory:',
    }
}

