#### OIPA
--------
[![Build Status](https://travis-ci.org/zimmerman-zimmerman/OIPA.svg)](https://travis-ci.org/zimmerman-zimmerman/OIPA)
[![Coverage Status](https://coveralls.io/repos/openaid-IATI/OIPA/badge.svg?branch=develop&service=github)](https://coveralls.io/github/openaid-IATI/OIPA?branch=master)

OIPA is a data-engine, enabling IATI XML compliant data to be parsed and interfaced using an API.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about the IATA XML standard at: www.iatistandard.org


#### About the project
--------

* Web Site:         http://www.oipa.nl
* Authors:          [Zimmerman & Zimmerman ](https://www.zimmermanzimmerman.nl/)
* License:          AGPLv3 (see included [LICENSE](https://github.com/openaid-IATI/OIPA/blob/master/LICENSE.MD) file for full license)
* Github Repo:      https://github.com/openaid-IATI/OIPA/
* Bug Tracker:      https://github.com/openaid-IATI/OIPA/issues
* Documentation:    https://github.com/openaid-IATI/OIPA/wiki


#### Can I contribute?
--------

Yes please! We are mainly looking for coders to help on the project. If you are a coder simply  press *Fork* at the top of this github page and hack away.

#### Who is making use of OIPA?
--------

* Dutch Ministry of Foreign Affairs:         http://beta.openaid.nl
* UNESCO Transparency Portal:                http://opendata.unesco.org/
* UN-Habitat:                                http://open.unhabitat.org
* DFID Devtracker (jan. 2016)                http://devtracker.dfid.gov.uk/
* Mohinga AIMS                               http://mohinga.info/en/


#### How to install the development environment on [Vagrant](https://www.vagrantup.com/)
--------
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

Or install fabric locally: `sudo pip install fabric`

and run:

```#!bash
fab serve
```

and open your browser at `http://localhost:19088/`.

This setup includes supervisor runnning on background, log is stored at `/vagrant/OIPA/static/supervisor.log`.
