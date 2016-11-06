source ~/.env/bin/activate
# creates super user. Piping method is use to prevent shell prompts
echo "from django.contrib.auth.models import User; User.objects.create_superuser(email='vagrant@oipa.nl', username='vagrant', password='vagrant')" | /vagrant/OIPA/manage.py shell
deactivate