#!/bin/bash

# Create oipa db
Q1="CREATE DATABASE IF NOT EXISTS oipa;"
Q2="GRANT ALL PRIVILEGES ON oipa.* TO oipa@localhost IDENTIFIED BY 'oipa';"
Q3="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}"

mysql --user=root --password=oipa --execute="${SQL}"

# Run syncdb
sudo -u vagrant /home/vagrant/.env/bin/python /vagrant/OIPA/manage.py syncdb --noinput
sudo -u vagrant /home/vagrant/.env/bin/python /vagrant/OIPA/manage.py loaddata /vagrant/etc/superuser.json
