#!/bin/bash
# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to install NGINX and Certbot for SSL certificate management.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Install NGINX
if ask_for_confirmation "Do you want to install NGINX?"; then
  print_status "Installing NGINX..."
  sudo apt update
  sudo apt install nginx -y
else
  echo "Skipping NGINX installation."
fi

# Setup NGINX
if ask_for_confirmation "Do you want to set up NGINX configuration?"; then
  . ./scripts/setup/setup_nginx.sh
else
  echo "Skipping NGINX configuration setup."
fi

print_status "Done installing NGINX."

# Install Certbot
if ask_for_confirmation "Do you want to install Certbot?"; then
  print_status "Installing certbot..."
  sudo apt install software-properties-common -y
  sudo add-apt-repository universe -y
  sudo apt-get update -y
  sudo apt-get install certbot python3-certbot-nginx -y
else
  echo "Skipping Certbot installation."
fi

# Setup Certbot
if ask_for_confirmation "Do you want to set up Certbot configuration?"; then
  . ./scripts/setup/setup_ssl.sh
else
  echo "Skipping Certbot configuration setup."
fi

print_status "Done installing Certbot."
