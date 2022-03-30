# This file is responsible for installing python on the correct version required for this project.

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6

sudo apt-get update
sudo apt-get install python3-virtualenv

cd ../OIPA
virtualenv -p /usr/bin/python3 env

source env/bin/activate
pip install uwsgi
pip install -r requirements.txt
