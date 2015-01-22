import re
from fabric.api import local
from fabric.api import run
from fabric.api import env


def get_oipa_port():
    """
    Get OIPA ssh port from `vagrant ssh-config` command
    """
    result = local('vagrant ssh-config', capture=True)
    for line in result.split('\n'):
        match = re.findall(' Port (?P<port>\d+)', line)
        if len(match):
            return match[0]
    return None


def serve():
    """
    Serve django dev server on localhost:19088
    """

    port = get_oipa_port()

    if port is None:
        print("Can not find OIPA instance port. Abort.")
        return

    env.password = 'vagrant'
    env.use_ssh_config = True
    env.host_string = "vagrant@127.0.0.1:{port}".format(port=port)
    run('/home/vagrant/.env/bin/python /vagrant/OIPA/manage.py runserver 0.0.0.0:8080')
