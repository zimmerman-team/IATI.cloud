Server requirements
 - Linux based OS
 - Python 2.6.x or 2.7.x
 - MySQL 5.6 and up
 - Redis 2.8.9 and up (lower not tested). Running at the standard port 6379.
 - Python libraries: virtualenv and pip

At Zimmerman & Zimmerman we installed OIPA from a clean OS Debian 7 install. The steps we needed to do to get the requirements installed can be found here.

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

Clone OIPA from Github

    apt-get install git
    git clone https://github.com/openaid-IATI/OIPA-V2.1.git
    cd OIPA-V2.1/OIPA

Install OIPA's used python libraries
    pip install  --upgrade distribute
    pip install -r requirements.txt

    # if lxml install fails, install:
    # sudo apt-get install libxml2-dev
    # sudo apt-get install libxslt1-dev
    # sudo apt-get install python2.7-dev

Create local settings (MySQL settings etc.)

    cd OIPA
    vim local_settings.py

For local settings advice and an update script, feel free to contact us at apollo@zimmermanzimmerman.nl

Create/synchronize the OIPA database tables

    python manage.py syncdb

Run the site via Apache or Nginx

Dependable on your set-up


