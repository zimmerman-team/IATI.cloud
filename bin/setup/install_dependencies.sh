#!/bin/bash

sudo apt-get update

sudo apt-get install -y git
sudo apt-get install -y python-virtualenv
sudo apt-get install -y python-dev
sudo apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

sudo locale-gen nl_NL.UTF-8
sudo dpkg-reconfigure locales

# postgresql
sudo apt-get install -y sqlite3 # for tests
sudo apt-get install -y libsqlite3-dev # for tests
sudo apt-get install -y postgresql-9.5
sudo apt-get install -y postgresql-client
sudo apt-get install -y postgresql-server-dev-9.5
sudo apt-get install -y postgis
sudo apt-get install -y postgresql-9.5-postgis-2.3
sudo apt-get install -y postgresql-9.5-postgis-2.3-scripts
sudo apt-get install python-psycopg2
sudo apt-get install libpq-dev
# GEOS
sudo apt-get install -y binutils libproj-dev gdal-bin libgeos-3.4.2 libgeos-dev

# redis
sudo apt-get install -y redis-server

# pip dependencies
sudo pip install ipython
