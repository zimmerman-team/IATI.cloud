#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to initially create a Solr docker container,
generating the files,
and updating the newly generated solr cores.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

print_status "Setting up Solr..."
sudo docker pull bitnami/solr:9.8.1
sudo docker compose up solr -d
print_status "Starting Solr for the first time, generating all relevant files..."
sleep 60
sudo bash ./scripts/update_solr_cores.sh
sudo docker compose down

print_status "Done setting up Solr."
