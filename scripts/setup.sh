#!/bin/bash

# Import utility functions
source ./scripts/util.sh

# Check if the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or use sudo."
  exit 1
fi

# Help

helper $0 $1 \
    "$0
Used to set up the IATI.cloud repository.
Requires sudo access.

- Initialises submodules
- Sets up environment files
- Sets up additional swap memory
- Installs Docker
- Installs Cockpit (linux dashboard)
- Installs NGINX with SSL enabled
- Sets up Solr (must be done before stack can be activated)
- Sets up the IATI.cloud docker image
- Starts IATI.cloud

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

confirm_and_run() {
  local question="$1"
  local command="$2"
  local skip_message="$3"

  if ask_for_confirmation "$question"; then
    eval "$command"
  else
    echo "$skip_message"
  fi
}

confirm_and_run "Do you want to initialise the submodules?" ". ./scripts/setup/install_submodules.sh" "Skipping the submodules."
confirm_and_run "Do you want to set up the environment files?" ". ./scripts/setup/setup_environment.sh" "Skipping the environment."
confirm_and_run "Do you want to setup additional swap memory (recommended, requires 64GB free space)?" ". ./scripts/setup/setup_swap.sh" "Skipping swap memory setup."
confirm_and_run "Do you want to install Docker?" ". ./scripts/setup/install_docker.sh" "Skipping Docker installation."
confirm_and_run "Do you want to install Cockpit (linux dashboard)?" ". ./scripts/setup/install_cockpit.sh" "Skipping Cockpit."
confirm_and_run "Do you want to install NGINX with SSL enabled?" ". ./scripts/setup/install_nginx.sh" "Skipping NGINX."
confirm_and_run "Do you want to store Solr data on a mounted directory?" ". ./scripts/setup/setup_solr_mount_dir.sh" "Skipping Solr mount dir."
confirm_and_run "Do you want to set up Solr (must be done before stack can be activated)?" ". ./scripts/setup/setup_solr.sh" "Skipping Solr."
confirm_and_run "Do you want to set up the IATI.cloud docker image? If you choose the Y option, there will be a manual step: hit control+c when the image is fully built and running." "sudo docker compose up iaticloud --build" "Setup script is done, please set up your env, and run 'bash ./scripts/build.sh <MODE>' to build the project."
confirm_and_run "Setup script is done, do you want to start IATI.cloud?" "sudo docker compose up -d" "Setup script is done. Start iati.cloud using the './scripts/start.sh <MODE>' script, or simply with: 'sudo docker compose up -d'."

print_status "Setup completed."
