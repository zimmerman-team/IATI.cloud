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
cores=(activity budget dataset organisation publisher result transaction transaction_trimmed transaction_sdgs budget_split_by_sector)

# Ask the user if replication should be set up at all, default to yes
if ask_for_confirmation "Do you want to set up Solr Replication?"; then
  # Ask the user for their solr host, in format such as 10.0.0.1:8983/solr
  read -p "Enter your Solr allowedUrls host(s, multiple separated by a comma) (e.g., 10.0.0.1:8983/solr,10.0.0.2:8984/solr): " solr_hosts
  sudo docker exec "$solr_container_id" sed -i "s#<str name=\"allowUrls\">\${solr.allowUrls:}</str>#<str name=\"allowUrls\">\${solr.allowUrls:$solr_hosts}</str>#g" "$bitnami_solr/solr.xml"
  read -p "Enter your Solr replication target host (replication leader IP, e.g., '10.0.0.1' or 'solr' if both leader and follower run on the same machine): " solr_replication_target
  no_replication=false
else
  no_replication=true
  solr_role="leader"
fi
# Ask the user if this is a Solr Leader or Follower
if [ "$no_replication" == false ]; then
  read -p "Is this Solr Replication Leader or Follower? Note: anything other than follower is resolved as leader. (leader/follower) " solr_role
fi

setup_replication() {
  # Skip replication if not required
  if [ "$no_replication" == true ]; then
    print_status "Skipping Solr Replication setup."
    return
  fi

  replication_core=$1
  config="$bitnami_solr/$replication_core/conf/solrconfig.xml"
  echo "Config: $config"

  # Check if "requestHandler name="/replication" already exists in solrconfig.xml
  if sudo docker exec "$solr_container_id" grep -q '<requestHandler name="/replication"' $config; then
    print_status "Replication already set up for core: $replication_core"
    return
  fi
  # Define the string to be replaced
  source='  <requestHandler name="/query" class="solr.SearchHandler">'

  # Use shell escaping for newlines in the replacement strings
  follower='  <requestHandler name="/replication" class="solr.ReplicationHandler">\n    <lst name="slave">\n      <str name="masterUrl">http://REPL_HOST:8983/solr/REPL_CORE</str>\n      <str name="pollInterval">00:05:00</str>\n      <str name="httpBasicAuthUser">REPL_USER</str>\n      <str name="httpBasicAuthPassword">REPL_PASS</str>\n      <str name="compression">internal</str>\n    </lst>\n  </requestHandler>\n\n  <requestHandler name="/query" class="solr.SearchHandler">'
  leader='  <requestHandler name="/replication" class="solr.ReplicationHandler">\n    <lst name="master">\n      <str name="replicateAfter">commit</str>\n      <str name="replicateAfter">optimize</str>\n    </lst>\n  </requestHandler>\n\n  <requestHandler name="/query" class="solr.SearchHandler">'

  if [ "$solr_role" == "follower" ]; then
    # Use 'g' flag for global replacement if there are multiple occurrences, otherwise '1' for the first.
    # The 's' command uses '\n' to represent a newline in the replacement part.
    sed_val="s|$source|$follower|g"
  else
    sed_val="s|$source|$leader|g"
  fi

  # Update the configuration
  sudo docker exec "$solr_container_id" sed -i "$sed_val" "$config"
  if [ "$solr_role" == "follower" ]; then
    username=$(grep -E '^SOLR_ADMIN_USERNAME=' .env | cut -d '=' -f2 | tr -d '"')
    password=$(grep -E '^SOLR_ADMIN_PASSWORD=' .env | cut -d '=' -f2 | tr -d '"')
    sudo docker exec "$solr_container_id" sed -i "s#REPL_USER#$username#g" $config
    sudo docker exec "$solr_container_id" sed -i "s#REPL_PASS#$password#g" $config
    sudo docker exec "$solr_container_id" sed -i "s#REPL_HOST#$solr_replication_target#g" $config
    sudo docker exec "$solr_container_id" sed -i "s#REPL_CORE#$replication_core#g" $config
  fi
}

for core in "${cores[@]}"; do
  # Copy the managed schema
  src="./direct_indexing/solr/cores/$core/managed-schema"
  docker cp $src "$solr_container_id:$bitnami_solr/$core/conf/managed-schema.xml"

  # Setup replication if required, for the named core.
  setup_replication $core $solr
  # if core is 'publisher' continue
  if [ "$core" == "publisher" ]; then
    continue
  fi

  # Copy the managed schema for draft cores
  docker cp $src "$solr_container_id:$bitnami_solr/draft_$core/conf/managed-schema.xml"
  # Setup replication if required, for the draft version of the named core.
  setup_replication "draft_$core"

  # Update the activity data cores with a higher maxFields value
  content_cores=(activity budget result transaction)
  if [[ " ${content_cores[@]} " =~ " $core " ]]; then
    # Increase the "maxFields" value in solrconfig.xml for the core
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
  # Read the .env file and extract the value of SOLR_VOLUME or SOLR_FOLLOWER_VOLUME
  if [ -f .env ]; then
    if [ "$solr_role" == "follower" ]; then
      mounted_dir=$(grep -E '^SOLR_FOLLOWER_VOLUME=' .env | cut -d '=' -f2 | tr -d '"' | sed 's|/solr_follower_data$||')
      echo "Using the value of SOLR_FOLLOWER_VOLUME in the .env file is: $mounted_dir"
    else
      mounted_dir=$(grep -E '^SOLR_VOLUME=' .env | cut -d '=' -f2 | tr -d '"' | sed 's|/solr_data$||')
      echo "Using the value of SOLR_VOLUME in the .env file is: $mounted_dir"
    fi
  else
    echo ".env file not found, unable to show SOLR_VOLUME or SOLR_FOLLOWER_VOLUME value in .env."
    read -p "Enter your mounted directory: " mounted_dir
  fi
  
  if [ $no_replication == false ]; then
    chown_dir="$mounted_dir/solr_follower_data"
  else
    chown_dir="$mounted_dir/solr_data"
  fi
  sudo chown -R 1001:root $chown_dir
else
  print_status "Skipping updating the ownership value of the mounted solr directory."
fi

print_status "Done updating solr cores."
