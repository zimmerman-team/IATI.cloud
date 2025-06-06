#!/bin/bash

# script to reset solr
sudo docker compose down
env_dir=$(grep -E '^SOLR_VOLUME=' .env | cut -d '=' -f2 | tr -d '"')
sudo rm -rf $env_dir
sudo bash scripts/setup/setup_solr_mount_dir.sh
sudo bash scripts/setup/setup_solr.sh
sudo docker compose down
