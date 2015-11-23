#!/bin/bash
# todo: peer authentication with oipa user

sudo -u postgres bash -c "psql -c \"CREATE USER oipa WITH PASSWORD 'oipa';\""
sudo -u postgres bash -c "psql -c \"ALTER ROLE oipa SUPERUSER;\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE oipa;\""

# Run syncdb
sudo -H -u vagrant /home/vagrant/.env/bin/python /vagrant/OIPA/manage.py syncdb --noinput
sudo -H -u vagrant /home/vagrant/.env/bin/python /vagrant/OIPA/manage.py loaddata superuser.json
