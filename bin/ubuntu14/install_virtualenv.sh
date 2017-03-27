#!/bin/bash

if [ ! -d "/home/vagrant/.env/" ]; then
    echo "Creating virtualenv..."
    sudo -H -u vagrant virtualenv /home/vagrant/.env
    sudo -H -u vagrant /home/vagrant/.env/bin/pip install --upgrade pip
    sudo -H -u vagrant /home/vagrant/.env/bin/pip install -r /vagrant/OIPA/requirements.txt

    sudo -H -u vagrant echo "source ~/.env/bin/activate" >> /home/vagrant/.bashrc
else
    echo "Virtualenv already created."
fi