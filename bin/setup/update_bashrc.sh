#!/bin/bash

if grep -Fxq "cd /vagrant/OIPA" /home/vagrant/.bashrc; then
    echo "Updating ~/.bashrc..."
    sudo -u vagrant echo "cd /vagrant/OIPA" >> /home/vagrant/.bashrc
    sudo -u vagrant echo "echo 'Starting supervisor...'"
    sudo -u vagrant echo "python ./manage.py supervisor --daemonize --logfile static/supervisor.log"
    sudo -u vagrant echo "echo 'Started.'"
else
    echo "bashrc already updated"
fi
