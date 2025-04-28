#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to set up the nginx configuration for the host machine.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Setup NGINX configuration
print_status "Setting up NGINX configuration..."

# Consts
conf_source="./scripts/setup/nginx_host_machine"
sites_available="/etc/nginx/sites-available"
sites_enabled="/etc/nginx/sites-enabled/"

# datastore.iati.cloud
# Ask the user for the server name
if ask_for_confirmation "Do you want to set up iati-cloud?"; then
    read -rp "What is the iati.cloud server name as defined in the DNS records (for example, datastore.iati.cloud)?: " server_name
    sudo cp $conf_source/iati.cloud "$sites_available/iati-cloud"
    sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "$sites_available/iati-cloud"
    read -p "Re-Enter your solr username: " username
    read -sp "Re-Enter your solr password: " password
    encoded_base64=$(echo -n "$username:$password" | base64)
    sudo sed -i "s/REPL_AUTH/$encoded_base64/g" "$sites_available/iati-cloud"
    sudo ln -s "$sites_available/iati-cloud" $sites_enabled
else
    echo "Skipping iati-cloud setup."
fi

# flower
if ask_for_confirmation "Do you want to set up celery flower?"; then
    sudo cp $conf_source/flower "$sites_available/flower"
    sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "$sites_available/flower"
    sudo ln -s "$sites_available/flower" $sites_enabled
else
    echo "Skipping iati-cloud setup."
fi

# cockpit
if ask_for_confirmation "Do you want to set up the nginx configuration for cockpit?"; then
    if systemctl is-active --quiet cockpit.socket; then
        sudo cp $conf_source/cockpit "$sites_available/cockpit"
        sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "$sites_available/cockpit"
        sudo ln -s "$sites_available/cockpit" $sites_enabled
    else
        echo "Cockpit is not installed or not active."
    fi
fi

# Redirect for old iati.cloud url
if ask_for_confirmation "Do you want to set up the redirect for iati.cloud -> datastore.iati.cloud?: "; then
  sudo cp $conf_source/iati.cloud-redirect "/etc/nginx/sites-available/iati-cloud-redirect"
  sudo ln -s "/etc/nginx/sites-available/iati-cloud-redirect" /etc/nginx/sites-enabled/
fi

# Restart nginx
print_status "Restarting NGINX..."
sudo service nginx restart

print_status "NGINX configuration setup complete."
