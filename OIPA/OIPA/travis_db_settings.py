from OIPA.production_settings import *  # noqa: F401, F403

SECRET_KEY = 'j!bxt0h-=d)1@2r8du!+e4m9x-y*5od7+zq&=tfjwq(ecuov!*'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}
