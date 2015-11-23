import re
from invoke import run, task, env


def get_oipa_port():
    """
    Get OIPA ssh port from `vagrant ssh-config` command
    """
    result = run('vagrant ssh-config')
    for line in result.stdout.split('\n'):
        match = re.findall(' Port (?P<port>\d+)', line)
        if len(match):
            return match[0]
    return None

@task
def test():
    """
    Run tests
    """
    run('./manage.py test --settings OIPA.test_settings --nomigrations')

@task
def serve():
    """
    Serve django dev server on localhost:19088
    """

    port = get_oipa_port()

    if port is None:
        print("Can not find OIPA instance port. Abort.")
        return

    run('vagrant ssh -c "cd /vagrant/OIPA/ && /home/vagrant/.env/bin/python manage.py runserver 0.0.0.0:8000"')
