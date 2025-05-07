#!/bin/bash

# Import utility functions
source ./scripts/util.sh

# Ensure this script is run as a root or sudo user
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

helper $0 $1 \
    "$0
Script is used to update the Solr cores with new schemas and XSLT configurations.
The script will copy over all of the managed schemas and xslt transformers.
Finally, it updates the ownership of the solr configuration files to 1001:root.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Ask the user if they are sure they want to copy these schemas, if not exit
read -p "Do you want to copy the schemas? (y/N) " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting..."
    exit 1
fi

print_status "Updating Solr cores with new schemas and XSLT configurations..."

echo "Active docker containers:"
docker ps

echo "Please enter your docker 'CONTAINER ID' for the active Solr container with the image bitnami/solr:"
read solr_container_id

# Update the managed-schema and xslt files for all cores
bitnami_solr=/bitnami/solr/server/solr
cores=(activity budget dataset organisation publisher result transaction transaction_trimmed transaction_sdgs budget_split_by_sector fcdo_budget)

for core in "${cores[@]}"; do
  src="./direct_indexing/solr/cores/$core/managed-schema"
  docker cp $src "$solr_container_id:$bitnami_solr/$core/conf/managed-schema.xml"
  # if core is 'publisher' continue
  if [[ "$core" == "publisher" || "$core" == "fcdo_budget" ]]; then
    continue
  fi
  docker cp $src "$solr_container_id:$bitnami_solr/draft_$core/conf/managed-schema.xml"

  # Update the activity data cores with a higher maxFields value
  content_cores=(activity budget result transaction)
  if [[ " ${content_cores[@]} " =~ " $core " ]]; then
    sed_val='s/<int name="maxFields">1000<\/int>/<int name="maxFields">2000<\/int>/'
    sudo docker exec "$solr_container_id" sed -i "$sed_val" "$bitnami_solr/$core/conf/solrconfig.xml"
    sudo docker exec "$solr_container_id" sed -i "$sed_val" "$bitnami_solr/draft_$core/conf/solrconfig.xml"
  fi
done

# Copy xslt separately for activity and draft_activity
xslt_dir="./direct_indexing/solr/cores/activity/xslt"
docker cp $xslt_dir "$solr_container_id:$bitnami_solr/activity/conf/"
docker cp $xslt_dir "$solr_container_id:$bitnami_solr/draft_activity/conf/"

# Ask the user if this is mounted locally, default to no. If it is, chown the files to 1001:root
if ask_for_confirmation "Are the files locally mounted (f.ex. on extra mounted volume)?"; then
  df -h
  # Read the .env file and extract the value of SOLR_VOLUME
  if [ -f .env ]; then
    mounted_dir=$(grep -E '^SOLR_VOLUME=' .env | cut -d '=' -f2 | tr -d '"' | sed 's|/solr_data$||')
    echo "Using the value of SOLR_VOLUME in the .env file is: $SOLR_VOLUME"
  else
    echo ".env file not found, unable to show SOLR_VOLUME value in .env."
    read -p "Enter your mounted directory: " mounted_dir
  fi
  sudo chown -R 1001:root $mounted_dir/solr_data
else
  print_status "Skipping updating the ownership value of the mounted solr directory."
fi

print_status "Done updating solr cores."
