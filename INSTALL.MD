Server requirements:
 - Linux based OS
 - Python 2.7.x
 - MySQL 5.6 and up
 - Redis 2.8.9 and up (lower not tested). Running at the standard port 6379. (package redis-server)
 - Python libraries: virtualenv and pip
 - Geodjango libraries: binutils libproj-dev gdal-bin libgeos-3.4.2 libgeos-dev
 - Libxml libraries: libxml2-dev  libxslt1-dev python2.7-dev


Install OIPA:

Add a new user to install a python virtual interpreter to.

    adduser oipa

Create the virtual interpreter and create / go to a folder to install OIPA in.

    apt-get install python-virtualenv
    cd /home/oipa/
    virtualenv oipav21
    cd oipav21
    source bin/activate
    cd /var/www/
    mkdir oipav21
    cd oipav21

Clone OIPA from Github (preferably with ssh, example below uses https)

    apt-get install git
    git clone https://github.com/openaid-IATI/OIPA-V2.1.git
    cd OIPA-V2.1/OIPA

Install OIPA's used python libraries

    pip install  --upgrade distribute
    pip install -r requirements.txt

Create local settings (MySQL settings etc.)

    vim OIPA/local_settings.py

For local settings advice and an update script, feel free to contact us via Twitter @zimmzimmerman 

Create/synchronize the OIPA database tables

    python manage.py syncdb

Run the site via Apache or Nginx, dependable on your set-up

Start the task queue with;

    python manage.py supervisor




