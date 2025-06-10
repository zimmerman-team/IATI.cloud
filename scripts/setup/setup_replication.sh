#!/bin/bash

# Import utility functions
source ./scripts/util.sh


helper $0 $1 \
    "$0
Used to set up Solr Replication.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

if ask_for_confirmation "Do you want to set up a mounted solr directory?"; then
  if [ -f .env ]; then
    mounted_dir=$(grep -E '^SOLR_FOLLOWER_VOLUME=' .env | cut -d '=' -f2 | tr -d '"' | sed 's|/solr_data$||')
    echo "Using the value of SOLR_FOLLOWER_VOLUME in the .env file is: $mounted_dir"
  else
    echo ".env file not found, unable to show SOLR_FOLLOWER_VOLUME value in .env."
    read -p "Enter your mounted directory root, where a 'solr_data' directory will be created: " mounted_dir
  fi
  sudo mkdir -p $mounted_dir/solr_follower_data
  sudo chown -R 1001:root $mounted_dir/solr_follower_data/
  sed -i "s|SOLR_FOLLOWER_VOLUME=solr_follower_data|SOLR_FOLLOWER_VOLUME=$mounted_dir/solr_follower_data|g" .env
else
  echo "Skipping mounted solr directory."
fi

print_status "Setting up Solr Replication..."
sudo docker pull bitnami/solr:9.8.1
sudo docker compose up solr-replication -d
print_status "Starting Solr Replication for the first time, generating all relevant files..."
sleep 60
sudo bash ./scripts/update_solr_cores.sh
sudo docker compose down

print_status "Done setting up Solr."
