## OIPA
--------
[![Build Status](https://travis-ci.org/zimmerman-zimmerman/OIPA.svg?branch=develop)](https://travis-ci.org/zimmerman-zimmerman/OIPA)
[![Coverage Status](https://coveralls.io/repos/zimmerman-zimmerman/OIPA/badge.svg?branch=develop&service=github)](https://coveralls.io/github/zimmerman-zimmerman/OIPA?branch=develop)
[![Requirements Status](https://requires.io/github/zimmerman-zimmerman/OIPA/requirements.svg?branch=develop)](https://requires.io/github/zimmerman-zimmerman/OIPA/requirements/?branch=develop)
[![Documentation Status](https://readthedocs.org/projects/oipa-docs/badge/?version=latest)](http://docs.oipa.nl/en/latest/?badge=latest)


OIPA extracts all published IATI XML files from the [IATI Registry](http://www.iatiregistry.org/publisher) and makes them available in a normalised PostgreSQL database, that you can access using a RESTful API.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about the IATA XML standard at: <a href="http://www.iatistandard.org" target="_blank">www.iatistandard.org</a>


## Documentation
--------

Documentation on installing, running and using OIPA can be found at <a href="http://docs.oipa.nl" target="_blank">docs.oipa.nl</a>


## Quick start
-------

1. Install [Vagrant](https://www.vagrantup.com/)
2. Run ```vagrant up```
3. Find your way into the machine: ```vagrant ssh```
4. Start the server: ```./manage.py runserver 0.0.0.0:8000```
5. Open your browser at <a href="http://localhost:8000" target="_blank">localhost:8000</a>


For more detailed informtion, see the [install documentation](http://docs.oipa.nl/en/latest/installing/)


## About the project
--------
* Website:         <a href="https://www.oipa.nl" target="_blank">oipa.nl</a>
* Authors:          <a href="https://www.zimmermanzimmerman.nl/" target="_blank">Zimmerman & Zimmerman</a>
* License:          AGPLv3 (see included <a href="https://github.com/openaid-IATI/OIPA/blob/master/LICENSE.MD" target="_blank">LICENSE</a> file for full license)
* Github Repo:      <a href="https://github.com/zimmerman-zimmerman/OIPA/" target="_blank">github.com/openaid-IATI/OIPA/</a>
* Bug Tracker:      <a href="https://github.com/zimmerman-zimmerman/OIPA/issues" target="_blank">github.com/openaid-IATI/OIPA/issues</a>
* Documentation:    <a href="https://github.com/zimmerman-zimmerman/OIPA/wiki" target="_blank">docs.oipa.nl</a>


## Can I contribute?
--------

Yes please! We are mainly looking for coders to help on the project. If you are a coder feel free to *Fork* the repository and send us Pull requests!

## Running the tests
-------
To run the tests, log into the vagrant machine and run:

```./manage.py test --nomigrations --settings=OIPA.test_settings```


## Who makes use of OIPA?
--------
* Dutch Ministry of Foreign Affairs:         <a href="https://www.openaid.nl" target="_blank">www.openaid.nl</a>
* IATI Studio:                               <a href="https://www.iatistudio.com/" target="_blank">www.iatistudio.com</a>
* DFID Devtracker:                           <a href="https://devtracker.dfid.gov.uk/" target="_blank">devtracker.dfid.gov.uk</a>
* UNESCO Transparency Portal:                <a href="http://opendata.unesco.org" target="_blank">opendata.unesco.org</a>
* UN-Habitat:                                <a href="http://open.unhabitat.org" target="_blank">open.unhabitat.org</a>
* Netherlands Enterprise Agency:             <a href="https://aiddata.rvo.nl/" target="_blank">aiddata.rvo.nl</a>
* Mohinga AIMS:                              <a href="http://mohinga.info/en/" target="_blank">mohinga.info</a>
