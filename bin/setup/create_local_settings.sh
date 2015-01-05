#!/bin/bash

# Generate secret key and create local_settings.py with this key
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
sudo -u vagrant sed -e "s/__SECRET_KEY__/${NEW_UUID}/g" /vagrant/etc/local_settings.py > /vagrant/OIPA/OIPA/local_settings.py