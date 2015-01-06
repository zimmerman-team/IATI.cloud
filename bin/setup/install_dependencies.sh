#!/bin/bash

sudo apt-get update

sudo apt-get install -y python-virtualenv
sudo apt-get install -y python-dev
sudo apt-get install -y libxml2-dev libxslt1-dev

# mysql-5.6
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password oipa'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password oipa'

sudo apt-get install -y libmysqld-dev
sudo apt-get install -y mysql-server-5.6

# GEOS
sudo apt-get install -y binutils libproj-dev gdal-bin libgeos-3.4.2 libgeos-dev

# redis
sudo apt-get install -y redis-server
