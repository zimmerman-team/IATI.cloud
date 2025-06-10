# Installing IATI.cloud locally with all dependencies

- [Installing IATI.cloud locally with all dependencies](#installing-iaticloud-locally-with-all-dependencies)
  - [Introduction](#introduction)
  - [Installation of dependencies](#installation-of-dependencies)
    - [Install python](#install-python)
    - [Install PostgreSQL](#install-postgresql)
    - [Install MongoDB](#install-mongodb)
    - [Install RabbitMQ](#install-rabbitmq)
    - [Install Solr](#install-solr)
  - [Setup](#setup)
    - [Dependencies](#dependencies)
    - [.env](#env)
    - [Python](#python)
    - [PostgreSQL](#postgresql)
  - [Running IATI.cloud manually](#running-iaticloud-manually)
  - [Usage](#usage)

---

## Introduction

The following is split up into two sections. The first is an [installation](#installation-of-dependencies) guide to the services that are required for IATI.cloud, like python and solr. However historically we have seen that across systems installations differ nearly every time, and therefore this guide is not considered complete. Use it as a guideline, rather than a step by step guide. Of course, google is your friend, and installation guides can be found for most if not all systems.

The second part is a [setup](#setup) guide, which explains which steps to take to get your IATI.cloud instance up and running.

Alternatively, you can use docker locally as well. [Read more about our docker setup](./DOCKER.md).

## Installation of dependencies

### Install python

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update 
sudo apt install python3.11
```

### Install PostgreSQL

```bash
sudo apt-get install postgresql
sudo systemctl enable postgresql.service
```

### Install MongoDB

```bash
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt install -y mongodb
sudo systemctl enable mongod.service
```

### Install RabbitMQ

```bash
sudo apt-get install -y erlang
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server.service
```

[if there are issues with installing rabbitmq](https://computingforgeeks.com/how-to-install-latest-rabbitmq-server-on-ubuntu-linux/)

### Install Solr

```bash
# Install java
sudo apt-get update
sudo apt-get install openjdk-11-jdk openjdk-11-jre
cat >> /etc/environment <<EOL
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
JRE_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre
EOL
# Install solr
cd /opt
wget https://archive.apache.org/dist/lucene/solr/9.8.1/solr-9.8.1.tgz
tar xzf solr-9.8.1.tgz solr-9.8.1/bin/install_solr_service.sh --strip-components=2
sudo bash ./install_solr_service.sh solr-9.8.1.tgz 

# Create required solr cores
sudo su - solr -c "/opt/solr/bin/solr create -c activity -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c budget -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c dataset -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c organisation -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c publisher -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c result -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c transaction -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c draft_activity -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c draft_budget -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c draft_result -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c draft_transaction -n data_driven_schema_configs"

sudo cp ./direct_indexing/solr/cores/activity/managed-schema /var/solr/data/activity/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/budget/managed-schema /var/solr/data/budget/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/dataset/managed-schema /var/solr/data/dataset/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/organisation/managed-schema /var/solr/data/organisation/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/publisher/managed-schema /var/solr/data/publisher/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/result/managed-schema /var/solr/data/result/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/transaction/managed-schema /var/solr/data/transaction/conf/managed-schema.xml
sudo cp -r ./direct_indexing/solr/cores/activity/xslt /var/solr/data/activity/conf/
sudo cp ./direct_indexing/solr/cores/activity/managed-schema /var/solr/data/draft_activity/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/budget/managed-schema /var/solr/data/draft_budget/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/result/managed-schema /var/solr/data/draft_result/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/transaction/managed-schema /var/solr/data/draft_transaction/conf/managed-schema.xml

sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/activity/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/budget/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/result/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/transaction/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/draft_activity/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/draft_budget/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/draft_result/conf/solrconfig.xml
sudo sed -i 's/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/' /var/solr/data/draft_transaction/conf/solrconfig.xml
```

Then, run `nano /opt/solr/bin/solr` and add `SOLR_JAVA_MEM="-Xms20g -Xmx20g"` or alternatively, however much memory you choose to assign.
Then, run `nano /opt/solr/server/etc/jetty.xml` and change in *LINE 71*: `<Set name="requestHeaderSize"><Property name="solr.jetty.request.header.size" default="8192" /></Set>` TO `<Set name="requestHeaderSize"><Property name="solr.jetty.request.header.size" default="65535" /></Set>`

And restart Solr

```bash
sudo service solr restart
```

## Setup

### Dependencies

Ensure the following services are running:

- Solr
- MongoDB
- PostgreSQL
- RabbitMQ

### .env

Make sure to set up your local .env file, we've provided an example under [.env.example.local](../.env.example.local).
The following is a table of fields in the .env file, their function and whether or not to change them.

| Field name | Subsystem | Functionality | Changeable (No/Optional/Must) |
| --- | --- | --- | --- |
| `SECRET_KEY` | Django | Secret key | Must |
| `DEBUG` | Django | Impacts django settings | Optional: change on production to False |
| `FRESH` | Direct Indexing | Determines if a new dataset is downloaded| Optional |
| `THROTTLE_DATASET` | Direct Indexing | Reduces the number of datasets indexed, can be used to have a fast local run of the indexing process. | Optional: False in production |
| `DJANGO_STATIC_ROOT` | Django | Determines where Django static files are served | Optional: for local development |
| `DJANGO_STATIC_URL` | Django | Determines where Django static files are served | Optional: for local development |
| `POSTGRES_HOST` | Postgres | Host ip | Optional |
| `POSTGRES_PORT` | Postgres | Host port | Optional |
| `POSTGRES_DB` | Postgres | Initial db name | Optional |
| `POSTGRES_USER` | Postgres | Root user name | Must |
| `POSTGRES_PASSWORD` | Postgres | Root user pass | Must |
| `CELERY_BROKER_URL` | Celery | Connection to the message broker like RabbitMQ. Form: `ampq://<RABBITMQ HOST IP>` | Optional: Depends on your broker |
| `FCDO_INSTANCE` | Direct Indexing | Enables additional indexing features such as GBP conversion and JSON dump fields | Optional: enable on FCDO instances |
| `SOLR_ADMIN_USERNAME` | Solr | Admin username | Must |
| `SOLR_ADMIN_PASSWORD` | Solr | Admin password | Must |
| `SOLR_BASE_URL` | Solr | The connection string from python to solr. *(Substitute ports if necessary.)* Form with auth: `http://<SOLR_ADMIN_USERNAME>:<SOLR_ADMIN_PASSWORD>@<SOLR HOST IP>:8983/solr`, or without: `http://<SOLR HOST IP>:8983/solr` | Optional: If authentication is enabled |
| `SOLR_AUTH_ENCODED` | NGINX | A Base64 encoding of `<SOLR_ADMIN_USERNAME>:<SOLR_ADMIN_PASSWORD>`. We use [base64encode.org](https://www.base64encode.org/). | Must |
| `MEM_SOLR_MIN` | Solr | The minimum available Solr memory | Optional |
| `MEM_SOLR_MAX` | Solr | The maximum available Solr memory | Optional |
| `SOLR_VOLUME` | Solr | Either the 'docker volume' solr_data, or a local mount directory like "SOLR_VOLUME="/my/storage/iati.cloud/direct_indexing/solr_mount_dir" | Optional |
| `SOLR_FOLLOWER_VOLUME` | Solr | Either the 'docker volume' solr_follower_data, or a local mount directory like "SOLR_follower_VOLUME="/my/storage/iati.cloud/direct_indexing/solr_follower_mount_dir" | Optional |
| `CELERYFLOWER_USER` | Celery | Flower access | Must |
| `CELERYFLOWER_PASSWORD` | Celery | Flower access | Must |
| `DJANGO_SUPERUSER_USERNAME` | Django | Initial superuser account | Must |
| `DJANGO_SUPERUSER_PASSWORD` | Django | Initial superuser account | Must |
| `DJANGO_SUPERUSER_EMAIL` | Django | Initial superuser account | Must |
| `MONGO_INITDB_ROOT_USERNAME` | MongoDB | Initial superuser account | Must |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB | Initial superuser account | Must |
| `MONGO_INITDB_DATABASE` | MongoDB | Default MongoDB database. This is not changeable, but is required for the initialisation of MongoDB in fresh starts in docker. | No, this must remain `activities` |
| `MONGO_CONNECTION_STRING` | MongoDB | `mongodb://<MONGO_INITDB_ROOT_USERNAME>:<MONGO_INITDB_ROOT_PASSWORD>@<MONGO HOST IP>:27017` | Must |
| `IC_DOMAIN` | NGINX | The domain on which the current IATI.cloud setup is deployed, localhost in development, iati.cloud in production | Optional, in production with domain pointed at the server |
| `CSRF_TRUSTED_ORIGINS` | Django | Django trusted origins, like `https://iati.cloud` for iati.cloud. "A list of trusted origins for unsafe requests (e.g. POST)." | Must |

### Python

Install create a virtual environment

```bash
python3.11 -m venv ./env
```

Activate environment

```bash
source ./env/bin/activate
```

Upgrade pip

```bash
pip install --upgrade pip
```

### PostgreSQL

Create a PostgreSQL database with name, username and password (example default values below)

```bash
sudo -u postgres psql

create database iati_cloud;
create user iati_cloud with encrypted password 'oipa';
grant all privileges on database iati_cloud to iati_cloud;
```

Run the initial migration

```bash
python manage.py migrate
```

Create a Django Admin user

```bash
python manage.py createsuperuser
```

Enter a username and a password. Emails are not required but feel free to use yours.

Preload the legacy currency conversion with data

```bash
python manage.py loaddata ./services/iaticloud/data_preload/legacy_currency_convert_dump.json
```

## Running IATI.cloud manually

Run the django server:

```bash
python manage.py runserver
```

Run celery workers:

```bash
celery -A iaticloud worker -l INFO --concurrency=32 -n worker@%%h
```

Optionally run celery revoke queue:

```bash
celery -A iaticloud worker -l INFO -n revoke@%%h -Q revoke_queue
```

Optionally run celery aida workers

```bash
celery -A iaticloud worker -l INFO --concurrency=4 -n aida@%%h -Q aida_queue
```

Run celery beat

```bash
celery -A iaticloud beat -l INFO
```

Run celery flower

```bash
celery -A iaticloud flower -l INFO --port=5555
```

---

## Usage

*Check out the [Usage guide](./USAGE.md) for your next steps.*
