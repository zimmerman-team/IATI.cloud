## Platform requirements an dependencies
--------
OIPA has been tested and is known to run on Linux (Ubuntu 14.04 LTS). It will likely work fine on most UNIX systems. It also runs on Mac OS X (10.9+) though that's not recommended due to complexities with geo-spatial dependencies (you're better of using vagrant!). OIPA will not run at all under any version of Windows since some of the core dependencies don't allow it.

OIPA works under Python 2 version 2.7 or greater. It does not work under Python 3 (yet). OIPA used to run under MySQL and Postgres, but since we included Postgres FTS, it only runs under Postgres.

Core dependencies include:

- [Postgres 9.1+](http://www.postgresql.org/)
- [Redis](http://redis.io/)
- [Supervisor](https://github.com/Supervisor/supervisor/) 
- [GeoDjango dependencies: GEOS, PROJ.4, PostGIS](https://docs.djangoproject.com/en/1.9/ref/contrib/gis/install/)

When using the docs below these are all installed automatically. 


--------
## How to install the development environment on <a href="https://www.vagrantup.com/" target="_blank">Vagrant</a>
--------
Initial setup scripts and Vagrantfile included,
in order to setup new instance type following inside repository root directory:

```

vagrant up

```

Setup includes:

 - OIPA directory mounted into /vagrant on VM
 - all dependencies installed
 - PostgresSQL database created (name: `oipa`, user: `oipa`, password: `oipa`)
 - inital superuser created (name: `vagrant`, password: `vagrant`)

To start:

```

vagrant ssh
# ...logs you onto VM
./manage.py runserver 0.0.0.0:8000

```


and open your browser at `http://localhost:8000/`.

This setup includes supervisor runnning on background, log is stored at `/vagrant/OIPA/static/supervisor.log`.

--------
## How to install on Ubuntu
--------

To prevent the documentation on installing on Ubuntu to be deprecated and incomplete, we would like to point you to the scripts that Vagrant uses to build OIPA on a Ubuntu VM. We keep the Vagrant install up-to-date so running these scripts manually should also install OIPA correctly. 


The scripts can be found in the `bin/setup` folder and the order in which they are executed can be found in the file `Vagrantfile` in the repository root.  



