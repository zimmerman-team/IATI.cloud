# IATI.cloud

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=zimmerman-zimmerman_iati.cloud&metric=alert_status)](https://sonarcloud.io/dashboard?id=zimmerman-zimmerman_iati.cloud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open issues](https://img.shields.io/github/issues/zimmerman-zimmerman/OIPA.svg?style=flat)](https://github.com/zimmerman-team/iati.cloud/issues)
---

- [Introduction](#introduction)
- [Running and using IATI.cloud](#setting-up-running-and-using-iati-cloud)
- [Requirements](#requirements)
    - [Software](#software)
    - [Hardware](#hardware)
- [Central python packages](#central-python-packages)
- [Code management](#code-management)
- [Contributing](#contributing)
    - [How to contribute](#how-should-i-contribute)
- [Who uses IATI.cloud](#who-currently-makes-use-of-iaticloud)
- [Branches](#branches)

---
## Introduction
IATI.cloud extracts all published IATI XML files from the [IATI Registry](http://www.iatiregistry.org/publisher) and stores all data in Apache Solr cores, allowing for fast access.

IATI is a global aid transparency standard and it makes information about aid spending easier to access, re-use and understand the underlying data using a unified open standard. You can find more about the IATI data standard at: [www.iatistandard.org](www.iatistandard.org)

We have recently moved towards a Solr Only version of the IATI.cloud. If you are looking for the hybrid IATI.cloud with Django API and Solr API, you can find this under the branch `archive/iati-cloud-hybrid-django-solr`

You can install this codebase using Docker. Follow the Docker Guide for more information.

## Setting up, running and using IATI cloud
Running and setting up is split into two parts: docker and manual. Because of the extensiveness of these sections they are contained in their own files. We've also included a usage guide, as well as a guide to how the IATI.cloud processes data. Find them here:
- [Docker guide](./docs/DOCKER.md)
- [Local guide](./docs/LOCAL.md)
- [Usage guide](./docs/USAGE.md)
- [Data processing guide](./docs/PROCESSING.md)

## Requirements
### Software
|Software|Version (tested and working)|What is it for|
|---|---|---|
|Python|3.11|General runtime|
|PostgreSQL|LTS|Django and celery support|
|RabbitMQ|LTS|Messaging system for Celery|
|MongoDB|LTS|Aggregation support for Direct Indexing|
|Solr|8.11 or 9.1.1|Used for indexing IATI Data|
|(optional) Docker|LTS|Running full stack IATI.cloud|
|(optional) NGINX|LTS|Connection|

### Hardware
*Disk space*: Generally, around 500gb of disk space should be available for indexing the entire IATI dataset, especially if the json dump fields are active (with .env FCDO_INSTANCE=True). If not, you can get away with around 300GB.

*RAM*: Around 20GB of RAM has historically proven to be an issue, which led to us setting a RAM requirement of 40GB. [Here is a handy guide to setting up RAM Swap](https://linuxize.com/post/create-a-linux-swap-file/)

#### Local development
For local development, only a limited amount of disk space is required. The complete iati dataset unindexed is around 10GB, and you can limit the dataset indexing quite extensively, you can easily trim the size requirement down to less than 20GB, especially by limiting the datasets.

For local development, Docker and NGINX are not required, but docker is recommended to avoid system sided setup issues.

## Submodules
We make use of a single submodule, which contains a dump of the Django static files for the administration panel, as well as the IATI.cloud frontend and streamsaver (used to stream large files to a user).
To update the IATI.cloud frontend, create a fresh build from the [frontend repository](https://github.com/zimmerman-team/iati.cloud.frontend), and replace the files in the submodule.
Specifically, we include the `./build` folder, and copy the `./build/static/css`, `./build/static/js` and `./build/static/media` directories to the `static` submodule.

To update the Django administrator static files, [collect the django static](https://docs.djangoproject.com/en/4.1/ref/contrib/staticfiles/), and update the files.

Lastly, [StreamSaver](https://github.com/jimmywarting/StreamSaver.js) is used to stream large files to the user.

## Central python packages
*Django* is used to host a management interface for the Celery tasks, this was formerly used to host an API.

*celery*, combined with *flower*, *django-celery-beat*, and *django-celery-results* is used to manage multitask processing.

*psycopg2-binary* is used to connect to PostgreSQL.

*python-dotenv* is used for .env support.

*lxml* and *MechanicalSoup* are used for legacy working with XML Documents.

*pysolr*, *xmljson* and *pymongo* are used to support the direct indexing to Solr process.

## Code Management
*flake8* is used to maintain code quality in pep8 style

*isort* is used to maintain the imports

*pre-commit* is used to enforce commit styles in the form
```
feat: A new feature
fix: A bug fix
docs: Documentation only changes
style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
refactor: A code change that neither fixes a bug nor adds a feature
perf: A code change that improves performance
test: Adding missing or correcting existing tests
chore: Changes to the build process or auxiliary tools and libraries such as documentation generation
```

## Contributing
### Can I contribute?
Yes! We are mainly looking for coders to help on the project. If you are a coder feel free to _Fork_ the repository and send us your amazing Pull Requests!

### How should I contribute?
Python already has clear PEP 8 code style guidelines, so it's difficult to add something to it, but there are certain key points to follow when contributing:
- PEP 8 code style guidelines should always be followed. Tested with `flake8 OIPA`.
- [Commitlint](https://github.com/conventional-changelog/commitlint#what-is-commitlint) is used to check your commit messages.
- Always try to reference issues in commit messages or pull requests ("related to #614", "closes #619" and etc.).
- Avoid huge code commits where the difference can not even be rendered by browser based web apps (Github for example). Smaller commits make it much easier to understand why and how the  changes were made, why (if) it results in certain bugs and etc.
- When developing a new feature, write at least some basic tests for it. This helps not to break other things in the future. Tests can be run with `pytest`
- If there's a reason to commit code that is commented out (there usually should be none), always leave a "FIXME" or "TODO" comment so it's clear for other developers why this was done.
- When using external dependencies that are not in PyPI (from Github for example), stick to a particular commit (i. e. `git+https://github.com/Supervisor/supervisor@ec495be4e28c694af1e41514e08c03cf6f1496c8#egg=supervisor`), so if the library is updated, it doesn't break everything
- Automatic code quality / testing checks (continuous integration tools) are implemented to check all these things automatically when pushing / merging new branches. Quality is the key!

## Who makes or made use of IATI.cloud?
- Dutch Ministry of Foreign Affairs: [www.openaid.nl](https://www.openaid.nl)
- Finnish Ministry of Foreign Affairs: [www.openaid.fi](https://www.openaid.fi)
- FCDO Devtracker: [devtracker.dfid.gov.uk](https://devtracker.dfid.gov.uk/)
- UNESCO Transparency Portal: [opendata.unesco.org](https://opendata.unesco.org)
- Netherlands Enterprise Agency: [aiddata.rvo.nl](https://aiddata.rvo.nl/)
- Mohinga AIMS: [mohinga.info](http://mohinga.info/en/)
- UN-Habitat: [open.unhabitat.org](http://open.unhabitat.org)
- Overseas Development Institute: [ODI.org](https://transparency.odi.org/)
- UN Migration: [IOM.int](https://www.iom.int/)
- AIDA [AIDA.tools](https://www.aida.tools/)

& many others

---
## Branches
- `main` - production ready codebase
- `develop` - completed but not yet released changes
- `archive/iati-cloud-hybrid-django-solr` - django based "OIPA" version of IATI.cloud. Decommissioned around halfway through 2022.

Other branches should be prefixed similarly to commits, like `docs/added-usage-readme`
