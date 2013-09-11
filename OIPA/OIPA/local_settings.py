# Django settings for OIPAv3 project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     # ('pp', 'vincent@zimmermanzimmerman.nl'),
)

SERVER_EMAIL = ''

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'oipav6',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'oipav3',
        'PASSWORD': 'Baksteen$$3',
        'HOST': '/Applications/MAMP/tmp/mysql/mysql.sock',
        # 'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '8889',                      # Set to empty string for default.
    }
}



# Make this unique, and don't share it with anybody.
SECRET_KEY = '709)+!x8tujusgf**8v0l%t(u65p3haip^&l17k^t(i_r+csqd'
