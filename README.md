OIPA
============

![Build status](https://travis-ci.org/openaid-IATI/OIPA.svg?branch=master)
![Coverage Status](https://img.shields.io/coveralls/openaid-IATI/OIPA.svg)

OIPA is developed within the www.openaid.nl and www.openaidsearch.org platform and enables IATI standard compliant datasets to easily parse and interface that data using the OIPA framework that has been developed using a Django interface. It has been implemented for UN-Habitat at http://open.unhabitat.org and currently being developed for UNESCO.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about IATA standard at:

http://iatistandard.org/

OIPA is extended to support a variety of global health indicators published by UN-Habitat, The World Bank and other sources of statistics.

OIPA is licensed under the GNU AGPL license.

Check the full documentation and how to use OIPA here: http://www.oipa.nl/

Codebase maintained by team Zimmerman & Zimmerman in Amsterdam.

============

Development on [Vagrant](https://www.vagrantup.com/)
========

Initial setup scripts and Vagrantfile included,
in order to setup new instance type following inside repository root directory:

```#!bash
vagrant up
```

Setup includes:
 - OIPA directory mounted into /vagrant on VM
 - all dependencies installed
 - mysql database created (name: `oipa`, user: `oipa`, password: `oipa`)
 - OIPA/local_settings.py file created
 - inital superuser created (name: `vagrant`, password: `vagrant`)

As this is not production ready setup, OIPA is not running as a service.

To start:

```#!bash
vagrant ssh
# ...logs you onto VM
./manage.py runserver 0.0.0.0:8080
```

and open your browser at `http://localhost:19088/`.

This setup includes supervisor runnning on background, log is stored at `/vagrant/OIPA/static/supervisor.log`.
