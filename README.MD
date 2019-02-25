## OIPA
--------

[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/66a6772e1f264199830b01a86f9a2b47)](https://www.codacy.com/app/eimantas_4/OIPA?utm_source=github.com&utm_medium=referral&utm_content=zimmerman-zimmerman/OIPA&utm_campaign=Badge_Coverage)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/zimmerman-zimmerman/OIPA/blob/master/LICENSE.MD)
![Open issues](https://img.shields.io/github/issues/zimmerman-zimmerman/OIPA.svg?style=flat)
[![CircleCI](https://circleci.com/gh/zimmerman-zimmerman/OIPA.svg?style=svg)](https://circleci.com/gh/zimmerman-zimmerman/OIPA)


OIPA extracts all published IATI XML files from the [IATI Registry](http://www.iatiregistry.org/publisher) and makes them available in a normalised PostgreSQL database, that you can access using a RESTful API.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about the IATI XML standard at: <a href="http://www.iatistandard.org" target="_blank">www.iatistandard.org</a>

## Requirements

| Name                   | Recommended version |
| ---                    | ---       |
| Python                 | 3.6.5     |
| PostgreSQL             | 9.6       |
| Redis                  | 4.0.x     |
| PostGIS                | See: <a href="https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/postgis/">installing PostGIS</a> |
| SpaciaLite (for tests) | See: <a href="https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/spatialite/">installing SpatiaLite</a> |


## Quick start

If you have Docker installed and want to be able to use OIPA right away, run:

```
docker-compose up
```

this will start a containerised (development) environment using Django's development server. Visit `0.0.0.0:8000` on your local browser. The superuser login credentials are `oipa` / `oipa`.

If you don't have Docker:

1. Go to your OIPA folder.
2. Run ```virtualenv <name> -p python3``` to create a virtual environment
3. Run ```source env/bin/activate``` to activate the virtual environment
4. Install required libraries using ```pip install -r requirements.txt```
5. Create a PostgreSQL database
6. Set your database credentials in ```OIPA/.env``` file as follows:
   * OIPA_DB_NAME= ```your_database_name```
   * OIPA_DB_USER= ```your_db_user```
   * OIPA_DB_PASSWORD= ```your_db_password```
7. Run database migrations with ```python manage.py migrate```
8. Start the development server: ```python manage.py runserver```
8. In order for the parser to work, you need to start Redis too: ```redis-server```
9. Create a superuser account: `python manage.py createsuperuser`
10. Start the process control centre (Supervisor): ```python manage.py supervisor```
11. Open your browser at <a href="http://localhost:8000" target="_blank">localhost:8000</a>
12. Follow instructions for signing-in: <a href="http://docs.oipa.nl/en/latest/admin_interface/" target="_blank">http://docs.oipa.nl/en/latest/admin_interface</a>
13. Finally, follow the instructions from here: <a href="http://docs.oipa.nl/en/latest/where_to_start/" target="_blank">http://docs.oipa.nl/en/latest/where_to_start</a>

Happy Hunting!

For more detailed information, see the [install documentation](http://docs.oipa.nl/en/latest/installing/)


## Full Documentation

Full documentation (which, at this point, needs an update) on installing, running and using OIPA can be found at <a href="http://docs.oipa.nl" target="_blank">docs.oipa.nl</a>


## About the project
* Website:         <a href="https://yoda.oipa.nl" target="_blank">yoda.oipa.nl</a>
* Authors:          <a href="https://www.zimmermanzimmerman.nl/" target="_blank">Zimmerman & Zimmerman</a>
* License:          AGPLv3 (see included <a href="https://github.com/zimmerman-zimmerman/OIPA/blob/master/LICENSE.MD" target="_blank">LICENSE</a> file for full license)
* Github Repo:      <a href="https://github.com/zimmerman-zimmerman/OIPA/" target="_blank">github.com/zimmerman-zimmerman/OIPA/</a>
* Bug Tracker:      <a href="https://github.com/zimmerman-zimmerman/OIPA/issues" target="_blank">github.com/zimmerman-zimmerman/OIPA/issues</a>
* Documentation:    <a href="https://github.com/zimmerman-zimmerman/OIPA/wiki" target="_blank">docs.oipa.nl</a>


## Can I contribute?

Yes please! We are mainly looking for coders to help on the project. If you are a coder feel free to *Fork* the repository and send us Pull requests!

## How should I contribute?

Python already has clear <a href="https://www.python.org/dev/peps/pep-0008/" target="_blank">PEP 8</a> code style guidelines, so it's difficult to add something to it, but there are certain key points to follow when contributing:

* <a href="https://www.python.org/dev/peps/pep-0008/" target="_blank">PEP 8</a> code style guidelines should _always_ be followed
* When making commits, in the first line try to summarize changes (in around 50 characters or less) and in the message body (if needed) try to explain _what_ you did, and, most importantly, _why_. Try to avoid commit messages like "Moving to Python 3" or "Fixed bugs". Other developers should be able to understand _why_ the change was made!
* Always try to reference issues ("related to #614", "closes #619" and etc.)
* Avoid huge code commits where the difference can not even be rendered by browser based web apps (Github for example). Smaller commit make it much easier to understand why the change was made, why (if) it resulted in certain bugs and etc
* When developing new feature, write at least some basic tests for it. This helps not to break other things in the future
* If there's a reason to commit code that is commented out (there usually should be none), always leave a "FIXME" or "TODO" comment so it's clear for other developers _why_ this was done
* When using external dependencies that are not in PyPI (from Github for example), stick to a particular commit (i. e. `git+https://github.com/Supervisor/supervisor@ec495be4e28c694af1e41514e08c03cf6f1496c8#egg=supervisor`), so if the library is updated, it doesn't break everything
* In the near future, automatic code quality / testing checks (continuous integration tools) will be implemented to check all these things automatically when pushing / merging new branches. Quality is the key!
* These rules are to be extended

## Running the tests
Pytest-django is used to run tests. This will be installed automatically when the project is set up.

To run tests, from the top level directory of the project, run ```pytest OIPA/```. If you are in the same directory where ```manage.py``` is, only running ```pytest``` will be sufficient. Refer to <a href="https://pytest-django.readthedocs.io/en/latest/#" target="_blank">Pytest-django documentations</a> for details.

Tip: to be able to use debuggers (f. ex. ipdb) with pytest, run it with `-s` option (to turn off capturing test output).

Testing / code quality settings can be found in the `setup.cfg` file. Test coverage settings (for pytest-cov plugin) can be found at `.coveragerc` file.


## Who makes use of OIPA?
* Dutch Ministry of Foreign Affairs:         <a href="https://www.openaid.nl" target="_blank">www.openaid.nl</a>
* IATI Studio:                               <a href="https://www.iatistudio.com/" target="_blank">www.iatistudio.com</a>
* DFID Devtracker:                           <a href="https://devtracker.dfid.gov.uk/" target="_blank">devtracker.dfid.gov.uk</a>
* UNESCO Transparency Portal:                <a href="https://opendata.unesco.org" target="_blank">opendata.unesco.org</a>
* UN-Habitat:                                <a href="http://open.unhabitat.org" target="_blank">open.unhabitat.org</a>
* Netherlands Enterprise Agency:             <a href="https://aiddata.rvo.nl/" target="_blank">aiddata.rvo.nl</a>
* Mohinga AIMS:                              <a href="http://mohinga.info/en/" target="_blank">mohinga.info</a>
* Overseas Development Institute:            <a href="https://transparency.odi.org/" target="_blank">ODI.org</a>
