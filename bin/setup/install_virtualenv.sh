#!/bin/bash

if [ ! -d "/home/vagrant/.env/" ]; then
    echo "Creating virtualenv..."
    sudo -u vagrant virtualenv /home/vagrant/.env
    sudo -u vagrant /home/vagrant/.env/bin/pip install -r OIPA/requirements.txt
    sudo -u vagrant /home/vagrant/.env/bin/pip install -r OIPA/test_requirements.txt

    sudo -u vagrant echo "source ~/.env/bin/activate" >> /home/vagrant/.bashrc
else
    echo "Virtualenv already created."
fi
