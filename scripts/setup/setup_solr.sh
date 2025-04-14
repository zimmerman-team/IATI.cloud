#!/bin/bash

print_status() {
    echo "

======================================================
                     Status Update
------------------------------------------------------
$1
======================================================
"
}

print_status "Setting up Solr..."

sudo docker pull bitnami/solr:9.8.1
sudo docker compose up solr -d
print_status "Starting Solr for the first time, generating all relevant files..."
sleep 60
sudo bash ./direct_indexing/solr/update_solr_cores.sh
sudo docker compose down

print_status "Done setting up Solr."
