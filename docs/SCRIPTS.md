# SCRIPTS

There are many scripts available. The following is a table displaying their function. For intricate details, use the -h or --help flag when running the script with bash, or simply open the scripts and read.

| Script name | Category | Function | Sudo (root access) required |
|---|---|---|---|
| [build.sh](../scripts/build.sh) | Docker core | Simple trigger for `docker compose build` | Yes |
| [clear_celery_queues.sh](../scripts/clear_celery_queues.sh) | Utility | Clear all items in all celery queues | Yes |
| [cov.sh](../scripts/cov.sh) | Development | Run the tests written for the ./direct_indexing module | No |
| [download_fcdo.sh](../scripts/download_fcdo.sh) | Utility | Based on requests by FCDO, re-downloads FCDO datasets | No |
| [restart.sh](../scripts/restart.sh) | Development | Restart the docker services based on the python code, to immediately utilise the latest code as written locally. | Yes |
| [select_env.sh](../scripts/select_env.sh) | Utility | Activates the desired environment in case of having multiple environments present. | No |
| [setup.sh](../scripts/setup.sh) | Setup | Main setup script, triggers subscripts after asking if they should be triggered | Yes |
| [setup/install_cockpit](../scripts/setup/install_cockpit.sh) | Setup | Installs `cockpit` | Yes |
| [setup/install_docker](../scripts/setup/install_docker.sh) | Setup | Installs `docker` | Yes |
| [setup/install_nginx](../scripts/setup/install_nginx.sh) | Setup | Installs `NGINX` and `Certbot`, optionally triggers nginx and certbot setups. | Yes |
| [setup/install_submodules](../scripts/setup/install_submodules.sh) | Setup | Inits and updates the git submodule, copies the static directory for the Django admin panel | No |
| [setup/setup_environment](../scripts/setup/setup_environment.sh) | Setup | Creates .env files, symlinks the selected one, requests information such as usernames and passwords and updates the .env files | No |
| [setup/setup_nginx](../scripts/setup/setup_nginx.sh) | Setup | Updates the machine's Nginx configuration with the required information | Yes |
| [setup/setup_solr_mount_dir](../scripts/setup/setup_solr_mount_dir.sh) | Setup | Creates the solr_data directory where the user wants to mount their solr data. | Yes |
| [setup/setup_solr_replication](../scripts/setup/setup_solr_replication.sh) | Setup | Creates the solr_replication_data directory where the user wants to mount their solr data. | Yes |
| [setup/setup_solr](../scripts/setup/setup_solr.sh) | Setup | Creates and triggers the configuration of the Solr docker image | Yes |
| [setup/setup_ssl](../scripts/setup/setup_ssl.sh) | Setup | Sets up SSL certificates for the Nginx configuration | Yes |
| [setup/setup_swap](../scripts/setup/setup_swap.sh) | Setup | Sets up swap space | Yes |
| [start.sh](../scripts/start.sh) | Docker core | Starts specified services | Yes |
| [stop.sh](../scripts/stop.sh) | Docker core | Stops specified services | Yes |
| [update_solr_cores.sh](../scripts/update_solr_cores.sh) | Utility | Updates the solr cores with updated configuration | Yes |
| [util.sh](../scripts/util.sh) | Utility | Contains utility functions for use across scripts directory, never accessed directly as it has no function | No |
