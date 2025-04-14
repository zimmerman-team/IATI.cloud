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

# Ask the user if this is mounted locally, default to no. If it is, chown the files to 1001:root
if ask_for_confirmation "Will the files be locally mounted (f.ex. on extra mounted volume)? You will be asked for the directory, where a ./solr directory will be created."; then
  df -h
  read -p "Enter your mounted directory: " mounted_dir
  sudo mkdir -p $mounted_dir/solr
  sudo chown -R 1001:root $mounted_dir/solr
else
  echo "Skipping mounted solr directory."
fi

sudo docker pull bitnami/solr:9.8.1
sudo docker compose up solr -d
sleep 60
sudo bash ./direct_indexing/solr/update_solr_cores.sh
sudo docker compose down

print_status "Done setting up Solr."
