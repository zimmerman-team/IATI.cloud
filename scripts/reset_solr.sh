#!/bin/bash

# script to reset solr
sudo docker compose down
sudo rm -rf ./direct_indexing/solr_data
sudo bash scripts/setup/setup_solr_mount_dir.sh
sudo bash scripts/setup/setup_solr.sh
sudo docker compose down
