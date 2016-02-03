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
./manage.py runserver 0.0.0.0:8000
```

Or install pyinvoke locally: `sudo pip install invoke`

and run:

```#!bash
invoke serve
```

and open your browser at `http://0.0.0.0:8000/`. 

Now start supervisor


This setup includes supervisor runnning on background, log is stored at `/vagrant/OIPA/static/supervisor.log`.
