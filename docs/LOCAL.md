# Installing IATI.cloud locally with all dependencies
- [Introduction](#introduction)
- [Installing dependencies](#installation-of-dependencies)
    - [Python](#install-python)
    - [Postgres](#install-postgresql)
    - [MongoDB](#install-mongodb)
    - [RabbitMQ](#install-rabbitmq)
    - [Solr](#install-solr)
- [Setup](#setup)
    - [.env](#env)
- [Running IATI.cloud](#running-iaticloud-manually)
- [Usage](#usage)

---
## Introduction
The following is split up into two sections. The first is an [installation](#installation) guide to the services that are required for IATI.cloud, like python and solr. However historically we have seen that across systems installations differ nearly every time, and therefore this guide is not considered complete. Use it as a guideline, rather than a step by step guide. Of course, google is your friend, and installation guides can be found for most if not all systems. 

The second part is a [setup](#setup) guide, which explains which steps to take to get your IATI.cloud instance up and running.

Alternatively, you can use docker locally as well. [Read more about our docker setup](./DOCKER.md).

## Installation of dependencies
### Install python
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update 
sudo apt install python3.11
```

### Install PostgreSQL
```
sudo apt-get install postgresql
sudo systemctl enable postgresql.service
```

### Install MongoDB
```
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt install -y mongodb
sudo systemctl enable mongod.service
```

### Install RabbitMQ
```
sudo apt-get install -y erlang
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server.service
```
[if there are issues with installing rabbitmq](https://computingforgeeks.com/how-to-install-latest-rabbitmq-server-on-ubuntu-linux/)

### Install Solr
```
sudo apt-get update
sudo apt-get install openjdk-11-jdk openjdk-11-jre
cat >> /etc/environment <<EOL
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
JRE_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre
EOL
cd /opt
wget https://archive.apache.org/dist/lucene/solr/9.1.1/solr-9.1.1.tgz
tar xzf solr-9.1.1.tgz solr-9.1.1/bin/install_solr_service.sh --strip-components=2
sudo bash ./install_solr_service.sh solr-9.1.1.tgz 

sudo su - solr -c "/opt/solr/bin/solr create -c activity -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c budget -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c dataset -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c organisation -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c publisher -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c result -n data_driven_schema_configs"
sudo su - solr -c "/opt/solr/bin/solr create -c transaction -n data_driven_schema_configs"

sudo cp ./direct_indexing/solr/cores/activity/managed-schema /var/solr/data/activity/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/budget/managed-schema /var/solr/data/budget/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/dataset/managed-schema /var/solr/data/dataset/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/organisation/managed-schema /var/solr/data/organisation/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/publisher/managed-schema /var/solr/data/publisher/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/result/managed-schema /var/solr/data/result/conf/managed-schema.xml
sudo cp ./direct_indexing/solr/cores/transaction/managed-schema /var/solr/data/transaction/conf/managed-schema.xml
sudo cp -r ./direct_indexing/solr/cores/activity/xslt /var/solr/data/activity/conf/
```

then ADD IN nano /opt/solr/bin/solr: SOLR_JAVA_MEM="-Xms20g -Xmx20g"

CHANGE IN nano /opt/solr/server/etc/jetty.xml LINE 71: `<Set name="requestHeaderSize"><Property name="solr.jetty.request.header.size" default="8192" /></Set>` TO `<Set name="requestHeaderSize"><Property name="solr.jetty.request.header.size" default="65535" /></Set>`

And restart solr
```
service solr restart
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
| `SOLR_BASE_URL` | Solr | The connection string from python to solr. _(Substitute ports if necessary.)_ Form with auth:<br />`http://<SOLR_ADMIN_USERNAME>:<SOLR_ADMIN_PASSWORD>@<SOLR HOST IP>:8983/solr`,<br />or without:<br />`http://<SOLR HOST IP>:8983/solr` | Optional: If authentication is enabled |
| `SOLR_AUTH_ENCODED` | NGINX | A Base64 encoding of `<SOLR_ADMIN_USERNAME>:<SOLR_ADMIN_PASSWORD>`. We use [base64encode.org](https://www.base64encode.org/). | Must |
| `CELERYFLOWER_PASSWORD` | Celery | Flower access | Must |
| `CELERYFLOWER_USER` | Celery | Flower access | Must |
| `DJANGO_SUPERUSER_USERNAME` | Django | Initial superuser account | Must |
| `DJANGO_SUPERUSER_PASSWORD` | Django | Initial superuser account | Must |
| `DJANGO_SUPERUSER_EMAIL` | Django | Initial superuser account | Must |
| `MONGO_INITDB_ROOT_USERNAME` | MongoDB | Initial superuser account | Must |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB | Initial superuser account | Must |
| `MONGO_INITDB_DATABASE` | MongoDB | Default MongoDB database. This is not changeable, but is required for the initialisation of MongoDB in fresh starts in docker. | No, this must remain `activities` |
| `MONGO_CONNECTION_STRING` | MongoDB | `mongodb://<MONGO_INITDB_ROOT_USERNAME>:<MONGO_INITDB_ROOT_PASSWORD>@<MONGO HOST IP>:27017` | Must |
| `IC_DOMAIN` | NGINX | The domain on which the current IATI.cloud setup is deployed, localhost in development, iati.cloud in production | Optional, in production with domain pointed at the server |


### Python
Install create a virtual environment
```
python3.11 -m venv ./env
```

Activate environment
```
source ./env/bin/activate
```

Upgrade pip
```
pip install --upgrade pip
```

### PostgreSQL
Create a PostgreSQL database with name, username and password (example default values below)
```
sudo -u postgres psql

create database iati_cloud;
create user iati_cloud with encrypted password 'oipa';
grant all privileges on database iati_cloud to iati_cloud;
```

Run the initial migration
```
python manage.py migrate
```

Create a Django Admin user
```
python manage.py createsuperuser
```
Enter a username and a password. Emails are not required but feel free to use yours.


Preload the legacy currency conversion with data
```
python manage.py loaddata ./services/iaticloud/data_preload/legacy_currency_convert_dump.json
```

## Running IATI.cloud manually
Run the django server:
```
python manage.py runserver
```

Run celery workers:
```
celery -A iaticloud worker -l INFO
```

Optionally rum celery revoke queue:
```
celery -A iaticloud worker -l INFO -n revoke@%%h -Q revoke_queue
```

Run celery beat
```
celery -A iaticloud beat -l INFO
```

Run celery flower
```
celery -A iaticloud flower -l INFO --port=5555
```

---
## Usage
<b>Check out the [Usage guide](./USAGE.md) for your next steps.</b>
