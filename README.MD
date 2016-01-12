#### OIPA
--------
[![Build Status](https://travis-ci.org/zimmerman-zimmerman/OIPA.svg?branch=develop)](https://travis-ci.org/zimmerman-zimmerman/OIPA)
[![Coverage Status](https://coveralls.io/repos/zimmerman-zimmerman/OIPA/badge.svg?branch=master&service=github)](https://coveralls.io/github/zimmerman-zimmerman/OIPA?branch=develop)
[![Requirements Status](https://requires.io/github/zimmerman-zimmerman/OIPA/requirements.svg?branch=develop)](https://requires.io/github/zimmerman-zimmerman/OIPA/requirements/?branch=develop)

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

#### Who makes use of OIPA?
--------

* Dutch Ministry of Foreign Affairs:         https://www.openaid.nl
* DFID Devtracker                            http://devtracker.dfid.gov.uk/
* UNESCO Transparency Portal:                http://opendata.unesco.org/
* UN-Habitat:                                http://open.unhabitat.org
* Netherlands Enterprise Agency:             http://aiddata.rvo.nl/
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
 - PostgresSQL database created (name: `oipa`, user: `oipa`, password: `oipa`)
 - inital superuser created (name: `vagrant`, password: `vagrant`)

To start:

```#!bash
vagrant ssh
# ...logs you onto VM
./manage.py runserver
```

Or install pyinvoke locally: `sudo pip install invoke`

and run:

```#!bash
invoke serve
```

and open your browser at `http://localhost:8000/`.

This setup includes supervisor runnning on background, log is stored at `/vagrant/OIPA/static/supervisor.log`.
