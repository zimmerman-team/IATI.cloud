#!/bin/bash

# Function to prompt user for Y/n choice
ask_for_confirmation() {
  read -rp "$1 (Y/n): " choice
  case "$choice" in
    ""|y|Y )
      return 0  # Default to Y if user presses Enter without typing anything
      ;;
    n|N )
      return 1
      ;;
    * )
      ask_for_confirmation "$1"  # Ask again if input is not recognized
      ;;
  esac
}

print_status() {
    echo "

======================================================
                     Status Update
------------------------------------------------------
$1
======================================================
"
}

# Install NGINX and Certbot
if ask_for_confirmation "Do NGINX and Certbot need to be installed before setup?"; then
  echo "Installing NGINX and Certbot..."
  print_status "Installing NGINX..."
  sudo apt update
  sudo apt install nginx -y

  print_status "Installing certbot..."
  sudo apt install software-properties-common -y
  sudo add-apt-repository universe -y
  sudo apt-get update -y
  sudo apt-get install certbot python3-certbot-nginx -y
else
  echo "Skipping NGINX and Certbot installation."
fi

# Install Cockpit
if ask_for_confirmation "Do you want to install Cockpit?"; then
  print_status "Installing Cockpit..."
  sudo apt install cockpit -y
  sudo systemctl enable --now cockpit.socket
else
  echo "Skipping Cockpit installation."
fi

# Configure nginx

print_status "Setting up NGINX configuration..."
# Function to configure NGINX for a given environment

# datastore.iati.cloud
# Ask the user for the server name
read -rp "What is the iati.cloud server name as defined in the DNS records (for example, datastore.iati.cloud)?: " server_name
sudo cp ./scripts/setup/nginx_host_machine/iati.cloud "/etc/nginx/sites-available/iati-cloud"
sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "/etc/nginx/sites-available/iati-cloud"
read -p "Re-Enter your solr username: " username
read -sp "Re-Enter your solr password: " password
encoded_base64=$(echo -n "$username:$password" | base64)
sudo sed -i "s/REPL_AUTH/$encoded_base64/g" "/etc/nginx/sites-available/iati-cloud"
sudo ln -s "/etc/nginx/sites-available/iati-cloud" /etc/nginx/sites-enabled/

# flower
sudo cp ./scripts/setup/nginx_host_machine/flower "/etc/nginx/sites-available/flower"
sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "/etc/nginx/sites-available/flower"
sudo ln -s "/etc/nginx/sites-available/flower" /etc/nginx/sites-enabled/

# cockpit
if systemctl is-active --quiet cockpit.socket; then
  sudo cp ./scripts/setup/nginx_host_machine/cockpit "/etc/nginx/sites-available/cockpit"
  sudo sed -i "s/REPL_SERVER_NAME/$server_name/g" "/etc/nginx/sites-available/cockpit"
  sudo ln -s "/etc/nginx/sites-available/cockpit" /etc/nginx/sites-enabled/
else
  echo "Cockpit is not installed or not active."
fi

# Redirect for old iati.cloud url
if ask_for_confirmation "Do you want to set up the redirect for iati.cloud -> datastore.iati.cloud?: "; then
  sudo cp ./scripts/setup/nginx_host_machine/iati.cloud-redirect "/etc/nginx/sites-available/iati-cloud-redirect"
  sudo ln -s "/etc/nginx/sites-available/iati-cloud-redirect" /etc/nginx/sites-enabled/
fi

# Restart nginx
print_status "Restarting NGINX..."
sudo service nginx restart

# SSL Certificates
print_status "Setting up SSL certificates..."
if ask_for_confirmation "Do you want to set up SSL certificates for your domains?"; then
  # Set up the ssl certificate, this will require some user input.
  echo "Setting up SSL certificates..."
  sudo certbot --nginx

  echo "Setting up cron job to renew SSL certificates..."
  # update crontab with `0 5 1 * * sudo certbot renew --preferred-challenges http-01`
  cron_command="0 5 1 * * sudo certbot renew --preferred-challenges http-01"
  temp_cron_file=$(mktemp)
  echo "$cron_command" > "$temp_cron_file"
  crontab "$temp_cron_file"
  rm "$temp_cron_file"
fi

print_status "Done installing NGINX."
