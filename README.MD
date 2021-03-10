# IATI.cloud

---
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=zimmerman-zimmerman_iati.cloud&metric=alert_status)](https://sonarcloud.io/dashboard?id=zimmerman-zimmerman_iati.cloud)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/zimmerman-zimmerman/OIPA/blob/master/LICENSE.MD)
[![Open issues](https://img.shields.io/github/issues/zimmerman-zimmerman/OIPA.svg?style=flat)](https://github.com/zimmerman-team/iati.cloud/issues)
[![CircleCI](https://circleci.com/gh/zimmerman-team/iati.cloud.svg?style=shield&circle-token=193a84b0736b82dd10d5e7bb0a118c2fc1c30273)](https://circleci.com/gh/zimmerman-team/iati.cloud)
---
IATI.cloud extracts all published IATI XML files from the [IATI Registry](http://www.iatiregistry.org/publisher) and makes them available in a normalised PostgreSQL database, that you can access using a RESTful API. The project also stores all the parsed data in Apache Solr cores, allowing for faster querying. Two APIs are currently encompassed by the IATI.cloud project.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about the IATI data standard at: [www.iatistandard.org](www.iatistandard.org)

## Requirements
| Name                   | Required version                                                                                                   | Installation instructions |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |---------------------------|
| Python                 | 3.6.5                                                                                                              | [Python 3.6.5](https://wiki.python.org/moin/BeginnersGuide/Download) <br /> Tip: for managing multiple versions of python you can use [pyenv](https://realpython.com/intro-to-pyenv/#why-not-use-system-python) |
| PostgreSQL             | latest                                                                                                             | [PostgreSQL](https://postgis.net/install/) |
| PostGIS                | latest | [PostGIS](https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/postgis/) <br /> Might already be installed depending on the PostgreSQL installation done |
| RabbitMQ               | latest                                                                                                             | [RabbitMQ](https://www.rabbitmq.com/download.html) |
| Apache Solr            | 8.2.0                                                                                                              | [Solr](https://lucene.apache.org/solr/guide/8_2/installing-solr.html) |
| Python requirements    | Installed by requirements.txt                                                                                      | See instructions below    |
| Diskspace              | 1GB of space is recommended to ensure the Repository, Postgres Database, Apache Solr and required services can be installed. Do keep in mind, parsing and indexing datasets does increase the overall size of the IATI.cloud project, which can reach up to or more than 80GB. | Not applicable |


## Setting up your IATI Cloud environment
1. Go to folder root/OIPA.<br>
2. Create a virtual environment with the correct Python version, recommended name is ‘env’ (ex: `virtualenv env -p python3` )
3. Activate the virtual environment (ex: `source env/bin/activate`)
4. Install required libraries using `pip install -r requirements.txt`
5. Make sure the following services are running on your installation: PostgreSQL,
(ex: `sudo systemctl status postgresql` )
6. Run `pre-commit install --hook-type commit-msg`
7. Create a PostgreSQL database
8. Add the following .env file to the current working directory:
```
OIPA_DB_NAME=oipa
OIPA_DB_USER=oipa
OIPA_DB_PASSWORD=oipa
DJANGO_SETTINGS_MODULE=OIPA.development_settings
```
9. Add the file “local_settings.py” with the following information to the folder root/OIPA/OIPA:
```
SOLR = {
  'indexing': True,
  'url': 'http://localhost:8983/solr',
  'cores': {
       'activity': 'activity',
       'budget': 'budget',
       'dataset': 'dataset',
       'organisation': 'organisation',
       'publisher': 'publisher',
       'result': 'result',
       'transaction': 'transaction',
  }
}
DOWNLOAD_DATASETS = False
```
10. Go back to the folder root/OIPA and run database migrations with the command `python manage.py migrate`
11. Start the development server with the command `python manage.py runserver`
12. Create a superuser account for django with the command `python manage.py createsuperuser`
13. Start RabbitMQ with `brew service start rabbitmq` on mac or `sudo service rabbitmq-server start` on linux.
14. Start Celery worker with the command: `celery -A OIPA worker --loglevel=info --concurrency=10`, change the concurrency to your liking.
15. Start Celery beat with the command: `celery -A OIPA beat --loglevel=info -S django`
16. Start Celery flower with the command: `celery flower -A OIPA --port=5555`
17. Navigate to your Solr installation.
18. To use Apache Solr you will need to create the following 7 cores:
- activity
- budget
- dataset
- organisation
- publisher
- result
- transaction

To create a core :
- Input the following command on the command line: `bin/solr create -c [name of your core]`.
- Copy the ‘managed-schema’ file from *OIPA/solr/[name of your core]/conf/* and paste it in the *server/solr/[name of your core]/conf/* folder of the solr core.
19. Run the command `bin/solr start` to run Solr.

You can now access the Django admin page at [http://localhost:8000/admin/](http://localhost:8000/admin/), the Flower Dashboard at [http://localhost:5555](http://localhost:5555) and the Apache Solr administrative dashboard at [localhost:8983/solr/#/](localhost:8983/solr/#/)

## Debugging Celery or Apache Solr
- install telnet
- add at the to-be-debugged line in your code :
```
from celery.contrib import rdb
rdb.set_trace()
```
When the code reaches the corresponding line, you will receive a notification in the terminal stating that they are waiting for the debugger at port [port number].<br>
In another terminal you can then launch: `telnet localhost [port number]`.<br>
This will open the debugger.

## Parsing/indexing the data.
This process is managed from the [Django administration page](https://iati.cloud/admin/django_celery_beat/periodictask/).
The following is a step by step description of everything that needs to be done to load the data inside your local postgres database.

1. **Disable Apache Solr indexing** within OIPA/OIPA/local_settings.py by changing ‘indexing’: True to False.
2. On the django administration page, run the task to [import codelists](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.w85d58axjqo6).
    - Wait for this to finish.
3. On the django administration page, force run the task to [update exchange rates](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.k3f97g5tzow5).
    - Wait for this to finish.
    - Activate a scheduled version of this task, the task should be run monthly, not strictly necessary on a local installation.
4. **Enable Apache Solr indexing.**
5. On the django administration page, run the task to [import datasets](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.dp7yeu31dvb8).
    - In case you want to make use of the IATI validator, make sure that you set DOWNLOAD_DATASETS = True in OIA/OIPA/local_settings.py, so the IATI validator can be used.
    - Wait for this to finish.
6. Wait for the IATI Validator to finish its validation. We can check the status here. If no data is returned, it has finished.
7. If you want to parse [ALL available datasets](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.ssadsw2a054j ) use the following: On the django administration page, run the task to [validate the datasets](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.mp76m2mhagg6). If you want to parse a [specific organisation or a specific dataset](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.7qpe9q8ynsl6)  , use those tasks.
    - Wait for this to finish.
8. We can now parse and index the datasets that have been prepared in the previous steps. On the django administration page, run the task to parse all [datasets](https://docs.google.com/document/d/1ExDE7QU10DP7zkdRFi9PVJWQjpH84Yx6w3dYIP4RZ6k/edit#heading=h.ssadsw2a054j).
    - Wait for this to finish.

After this all the data is available within our database as well as Solr. Solr can now be used to query the data.
Simply select the core containing the information you're interested in, go to the query tab and ask your question.

## API Documentation
Full API documentation for iati.cloud can be found at [docs.iati.cloud](https://iati.cloud/documentation).

## About the project
- Website: [www.iati.cloud](https://www.iati.cloud)
- Authors: [Zimmerman B.V.](https://www.zimmermanzimmerman.nl/)
- License: AGPLv3 (see included [LICENSE](https://github.com/zimmerman-team/iati.cloud/blob/master/LICENSE.MD) file for full license)
- Github Repo: [github.com/zimmerman-zimmerman/iati.cloud/](https://github.com/zimmerman-team/iati.cloud/)
- Bug Tracker: [github.com/zimmerman-zimmerman/iati.cloud/issues](https://github.com/zimmerman-team/iati.cloud/issues)

## Can I contribute?
Yes! We are mainly looking for coders to help on the project. If you are a coder feel free to _Fork_ the repository and send us your amazing Pull Requests!

## How should I contribute?
Python already has clear PEP 8 code style guidelines, so it's difficult to add something to it, but there are certain key points to follow when contributing:
- PEP 8 code style guidelines should always be followed. Tested with `flake8 OIPA`.
- [Commitlint](https://github.com/conventional-changelog/commitlint#what-is-commitlint) is used to check your commit messages.
- Always try to reference issues in commit messages or pull requests ("related to #614", "closes #619" and etc.).
- Avoid huge code commits where the difference can not even be rendered by browser based web apps (Github for example). Smaller commits make it much easier to understand why and how the  changes were made, why (if) it results in certain bugs and etc.
- When developing a new feature, write at least some basic tests for it. This helps not to break other things in the future. Tests can be run with `pytest`
- If there's a reason to commit code that is commented out (there usually should be none), always leave a "FIXME" or "TODO" comment so it's clear for other developers why this was done.
- When using external dependencies that are not in PyPI (from Github for example), stick to a particular commit (i. e. `git+https://github.com/Supervisor/supervisor@ec495be4e28c694af1e41514e08c03cf6f1496c8#egg=supervisor`), so if the library is updated, it doesn't break everything
- Automatic code quality / testing checks (continuous integration tools) are implemented to check all these things automatically when pushing / merging new branches. Quality is the key!

## Running the tests
Pytest-django is used to run tests. This will be installed automatically when the project is set up.
To run tests, from the top level directory of the project, run `pytest OIPA/`. If you are in the same directory where `manage.py` is, only running `pytest` will be sufficient. Refer to [Pytest-django documentations](https://pytest-django.readthedocs.io/en/latest/#) for details.

Tip: to be able to use debuggers (f. ex. ipdb) with pytest, run it with `-s` option (to turn off capturing test output).

Testing / code quality settings can be found in the `setup.cfg` file. Test coverage settings (for pytest-cov plugin) can be found at `.coveragerc` file.

## Who currently makes use of IATI.cloud?
- Dutch Ministry of Foreign Affairs: [www.openaid.nl](https://www.openaid.nl)
- FCDO Devtracker: [devtracker.dfid.gov.uk](https://devtracker.dfid.gov.uk/)
- UNESCO Transparency Portal: [opendata.unesco.org](https://opendata.unesco.org)
- Netherlands Enterprise Agency: [aiddata.rvo.nl](https://aiddata.rvo.nl/)
- Mohinga AIMS: [mohinga.info](http://mohinga.info/en/)
- UN-Habitat: [open.unhabitat.org](http://open.unhabitat.org)
- Overseas Development Institute: [ODI.org](https://transparency.odi.org/)
- UN Migration: [IOM.int](https://www.iom.int/)
- AIDA [AIDA.tools](https://www.aida.tools/)


& many others
