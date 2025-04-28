#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to create a new solr_data directory for locally hosting IATI.cloud solr data,
rather than on a docker volume.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Set up mounted solr directory
print_status "Setting up mounted Solr directory..."

if ask_for_confirmation "Do you want to set up a mounted solr directory?"; then
  df -h
  read -p "Enter your mounted directory root, where a 'solr_data' directory will be created: " mounted_dir
  sudo mkdir -p $mounted_dir/solr_data
  sudo chown -R 1001:root $mounted_dir/solr_data/
  sed -i 's|SOLR_VOLUME=solr_data|SOLR_VOLUME="$mounted_dir/solr_data"|g' .env
else
  echo "Skipping mounted solr directory."
fi

print_status "Mounted Solr directory setup complete."
