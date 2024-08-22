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

sudo docker pull bitnami/solr:9.1.1
sudo docker compose up solr -d
sleep 60
sudo bash ./direct_indexing/solr/update_solr_cores.sh
sudo docker compose down

print_status "Done setting up Solr."
