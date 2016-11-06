Refresh the state of the systemd init system with this new uWSGI service on board

sudo systemctl daemon-reload

In order to start the script you'll need to run the following:

sudo systemctl start uwsgi

In order to start uWSGI on reboot, you will also need:

sudo systemctl enable uwsgi

You can use the following to check its status:

systemctl status uwsgi






sudo systemctl enable supervisor  