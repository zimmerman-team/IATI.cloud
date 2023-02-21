# Installing and running IATI.cloud with Docker
- [Introduction](#introduction)
- [Services](#services)
    - [Python](#install-python)
    - [Postgres](#install-postgresql)
    - [MongoDB](#install-mongodb)
    - [RabbitMQ](#install-rabbitmq)
    - [Solr](#install-solr)
- [Running](#running)
- [Docker usage](#docker-usage)
- [Usage](#usage)
- [Docker installation guide](#docker-installation-guide)

---
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
| database | database | 5432 | postgres:latest | Using the POSTGRES_ fields in .env to set up and access. `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, self-explanatory default values for the user, password and database name.<br />We mount `/var/lib/postgresql/data` to our `db_data` docker 'volume', which is persisted, meaning the container can be stopped and started without losing data. |
| rabbitmq | rabbitmq | 5672,15672 | rabbitmq:latest | We mount `/var/lib/rabbitmq` to our `rabbitmq_data` docker 'volume', which is persisted (as above). |
| mongo | mongo | 27017 | mongo:latest | Accessed through `mongodb://USER:PASS!@mongo:27017` where USER and PASS are set in the `MONGO_INITDB_` fields in .env.<br />We mount `/data/db` to our `mongo_data` docker 'volume', which is persisted (as above). |
| solr | solr | 8983 | bitnami/solr:9.1.1 | Using bitnami instead of default solr because of the env options. We're mounting the `/bitnami` directory to a local directory, which allows us to manipulate the core configuration. We pass SOLR_CORES with a list of all our cores. We pass `SOLR_OPTS` containing memory options. We're using `SOLR_ADMIN_USERNAME` and `*_PASSWORD` to use authentication. |
| iaticloud | iaticloud | 8000 | . (local Dockerfile) | We build a Docker image with our IATI.cloud codebase. This image installs the [requirements](../requirements.txt), Java 11 (for the Solr post tool), and runs the [entrypoint](../services/iaticloud/docker-entrypoint.sh). The entrypoint waits for the depended services to be fully started, then checks if this is the initial run of the IATI.cloud container. If not, it sets up the static files, sets up the database and sets up the superuser with the `DJANGO_SUPERUSER_*` .env variables. |
| celeryworker | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs main celery workers with N concurrency where N is the n.o. cores in the available CPU. |
| celeryrevokeworker | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs a single celery worker named Revoke to cancel all tasks |
| celeryscheduler | none | ports | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs celery beat |
| celeryflower | none | 5555 | . (local Dockerfile) | This runs on the `iaticloud` docker image. It runs celery flower task management interface, uses the password and username from CELERYFLOWER_ prefixed .env fields |
| nginx | nginx | 80 | ./services/nginx | Runs NGINX and enables the flower and datastore subdomains for a provided domain. For local development it also allows subdomains. Customize `SOLR_AUTH_ENCODED` and `IC_DOMAIN`. iati.cloud-redirect is available but not enabled by default. The docker image is more described [here](../services/nginx/NGINX.md). |

## Running
Ensure your .env is set up correctly, reference the .env.example.<br />

You can optionally run the following commands to gather the external images.
```
sudo docker pull rabbitmq
sudo docker pull postgres
sudo docker pull mongo
sudo docker pull bitnami/solr:9.1.1
sudo docker pull python:3.11
```

*Run the following once!*
Setting up persisted solr data:
```
sudo mkdir ./direct_indexing/solr_mount_dir
sudo chown 1001 ./direct_indexing/solr_mount_dir
sudo docker compose --env-file .env up solr
# AFTER STARTUP
sudo docker compose down
sudo bash ./direct_indexing/solr/update_solr_cores.sh
```

This is required for now, to be able to use our custom core configuration. We are waiting for a resolution for [this config issue](https://github.com/bitnami/containers/issues/24146) to move away from this.

## Docker usage
### First build
Running the docker containers (--build is optional because the local docker image needs to be built). This will allow the iaticloud/main docker image to be built and the django migrations etc. to be executed:
```
sudo docker compose --env-file .env up --build iaticloud
sudo docker compose down
```

once this image is built, build the nginx container (we can not do these together, as nginx depends on celery flower, which in turn depends on the iaticloud image being built.)
```
sudo docker compose --env-file .env up
```


Stopping the docker containers:
```
sudo docker compose --env-file .env down
```

### (Re)-starting 
```
sudo docker compose -d --env-file .env up
```

### After you've made changes to the iati.cloud codebase
```
sudo docker compose --env-file -d .env up --build
```

### After you've made changes to the Solr managed-schema file(s) in ./direct_indexing/solr/cores/_CORE_/
```
sudo direct_indexing/solr/update_solr_cores.sh
```
and restart the solr container, the changes should automatically be picked up.

### Removing built docker images
```
sudo docker images
sudo docker image rm <ID>
```

### Connecting to live docker containers 
```
sudo docker ps
sudo docker exec -i -t _<CONTAINER ID>_ /bin/bash
```

### Connecting to docker logs
```
sudo docker ps
sudo docker logs _<CONTAINER ID>_
```

### Other notes:
 - use `--detach` or `-d` to detach the docker containers from the current terminal.
 - use `--build` to rebuild the images.

---
## Usage
<b>Check out the [Usage guide](./USAGE.md) for your next steps.</b>

## Docker installation guide
### Linux
Install the prerequisites:
```
sudo apt-get install curl
sudo apt-get install gnupg
sudo apt-get install ca-certificates
sudo apt-get install lsb-release
```

Set up the docker gpg files
```
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install docker and docker compose:
```
sudo apt-get update

### Install docker and docker compose on Ubuntu
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

(optional:) Verify installation. You should see "This message shows that your installation appears to be working correctly."
```
sudo docker run hello-world
```