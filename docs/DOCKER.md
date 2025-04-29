# Installing and running IATI.cloud with Docker

- [Installing and running IATI.cloud with Docker](#installing-and-running-iaticloud-with-docker)
  - [Quick start](#quick-start)
  - [Introduction](#introduction)
  - [.env](#env)
  - [Services](#services)
  - [Setup](#setup)
  - [Docker usage](#docker-usage)
    - [Running basics](#running-basics)
    - [After docker service changes](#after-docker-service-changes)
    - [After changing solr configuration](#after-changing-solr-configuration)
    - [Removing built docker images](#removing-built-docker-images)
    - [Connecting to live docker containers](#connecting-to-live-docker-containers)
    - [Connecting to docker logs](#connecting-to-docker-logs)
    - [Other notes](#other-notes)
  - [Usage](#usage)

---

## Quick start

Run the setup script from the IATI.cloud root directory

```bash
sudo bash scripts/setup.sh
```

Notes:

- Answer with `Y` to the confirmation requests. This will ensure your setup will be complete and consistently reproducible.
- We recommend providing Solr with 40GB max memory, as we have seen lower values leading to crashing due to maxing out the provided memory at 20GB. Use swap memory if necessary (setup provided).
- Install Cockpit if installing on a server or even on a local linux machine, it is a helpful tool for machine maintenance.
- If on a server, do set up NGINX and SSL for access. Ensure a domain is prepared, such as `test.iati.cloud` or `iaticloud.example.com`.
- We recommend using a mounted directory for Solr storage, as it makes manipulation of the created cores much easier.
- For the environment, do not use symbols in the password.
- When prompted for a domain, follow the example provided. If the example contains http or https, include it in the value. If it does not, do not include it in the value.

## Introduction

We want to have a full stack IATI.cloud application with the above specifications running.
This includes Django, RabbitMQ and Celery, along with a postgres database, mongodb for aggregation, Apache Solr for document indexing, and lastly NGINX as a web server.

To accomplish this, we have created a [docker-compose](../docker-compose.yml) file, which starts all of the services. Each "cog in the system" is it's own runnable docker container.

The services use the default docker compose network. Each service registers itself to the network through the service name. This allows the docker containers to connect to eachother. Where locally you would use `localhost:5432`, a docker container connecting to a PostgreSQL container would refer to `database:5432`. By providing a port like `ports: 8000:8000`, you allow the localhost port 8000 to connect through to the docker container's port 8000.

## .env

Please check out the [reference of .env under the local docs](./LOCAL.md#env). They are the same with the exception of the host IPs which are the services as explained above.

## Services

| service | network name | ports | image | Additional notes |
|---|---|---|---|---|
| database | database | 5432 | postgres:latest | Using the POSTGRES_ fields in .env to set up and access. `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, self-explanatory default values for the user, password and database name. We mount `/var/lib/postgresql/data` to our `db_data` docker 'volume', which is persisted, meaning the container can be stopped and started without losing data. |
| rabbitmq | rabbitmq | 5672,15672 | rabbitmq:latest | We mount `/var/lib/rabbitmq` to our `rabbitmq_data` docker 'volume', which is persisted (as above). |
| mongo | mongo | 27017 | mongo:latest | Accessed through `mongodb://USER:PASS@mongo:27017` where USER and PASS are set in the `MONGO_INITDB_` fields in .env. We mount `/data/db` to our `mongo_data` docker 'volume', which is persisted (as above). |
| solr | solr | 8983 | bitnami/solr:9.1.1 | Using bitnami instead of default solr because of the env options. We're mounting the `/bitnami` directory to either the solr_data docker volume, or a local directory through the environment variable `SOLR_VOLUME`, which allows us to manipulate the core configuration. We pass SOLR_CORES with a list of all our cores. We pass `SOLR_OPTS` containing memory options. We're using `SOLR_ADMIN_USERNAME` and `*_PASSWORD` to use authentication. |
| iaticloud | iaticloud | 8000 | . (local Dockerfile) | We build a Docker image with our IATI.cloud codebase. This image installs the [requirements](../requirements.txt), Java 11 (for the Solr post tool), and runs the [entrypoint](../services/iaticloud/docker-entrypoint.sh). The entrypoint waits for the depended services to be fully started, then checks if this is the initial run of the IATI.cloud container. If not, it sets up the static files, sets up the database and sets up the superuser with the `DJANGO_SUPERUSER_*` .env variables. |
| celeryworker | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs main celery workers with N concurrency where N is the n.o. cores in the available CPU. |
| celeryrevokeworker | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs a single celery worker named Revoke to cancel all tasks |
| celeryscheduler | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs celery beat |
| celeryflower | none | 5555 | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs celery flower task management interface, uses the password and username from CELERYFLOWER_ prefixed .env fields |
| nginx | nginx | 80 | ./services/nginx | Runs NGINX and enables the flower and datastore subdomains for a provided domain. For local development it also allows subdomains. Customize `SOLR_AUTH_ENCODED` and `IC_DOMAIN`. iati.cloud-redirect is available but not enabled by default. The docker image is more described [here](../services/nginx/NGINX.md). |

## Setup

We recommend using the `./scripts/setup.sh` script to get everything set up for you, then running `sudo docker compose up -d` to start the required processes.

The following is a description of all the steps required to set up IATI.cloud through docker:

- Set up the git submodule for Django static
- Set up the environment file
- (o) Set up swap memory in case there is not enough RAM available.
- Install docker
- (o) Install cockpit (linux dashboard, for server maintenance)
- (o) Install NGINX and Certbot
- (o) Set up Solr data on a mounted directory (optional but highly **recommended** for stable manipulation of cores)
- Install Solr and set up the cores
- Initial build of `iaticloud` docker image, to ensure proper building for usage in all celery services.

If you are looking for manual steps to installation, follow the chain of function in the scripts starting at [setup.sh](../scripts/setup.sh), or read up on the scripts that are available in [the SCRIPTS documentation](./SCRIPTS.md).

## Docker usage

### Running basics

This assumes the setup has been done.

Start the entire stack with:

```bash
sudo docker compose up -d
```

Stopping the docker containers:

```bash
sudo docker compose down
```

Restarting

```bash
sudo docker compose down
sudo docker compose up -d
```

### After docker service changes

For example, after updating the version of PostgresDB.

```bash
sudo docker compose build <SERVICE_NAME>
```

### After changing solr configuration

For example, after changing the sector code from a `pdouble` to a `pint` in the `budget` core's `managed-schema` file.

```bash
sudo docker compose up -d solr
sudo direct_indexing/solr/update_solr_cores.sh
sudo docker compose down
```

_note: this should only be done on empty cores. otherwise, your core might be unable to start the updated core. Use the clear_all_cores task in Django admin._

### Removing built docker images

```bash
sudo docker images
sudo docker image rm <ID>
```

### Connecting to live docker containers

```bash
sudo docker exec -it <SERVICE_NAME> /bin/bash
```

### Connecting to docker logs

```bash
sudo docker logs <SERVICE_NAME>
```

or, to get live updating logs

```bash
sudo docker logs <SERVICE_NAME> -f
```

### Other notes

- use `--detach` or `-d` to detach the docker containers from the current terminal.
- use `--build` to rebuild the images.
- use `-f` to get live updates of logs.

---

## Usage

**Check out the [Usage guide](./USAGE.md) for your next steps.**
