#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to set up SSL certificates for the domains on the server,
alongside autorenewal of the certificates.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# SSL Certificates
print_status "Setting up SSL certificates..."
if ask_for_confirmation "Do you want to set up SSL certificates for your domains?"; then
  # Set up the ssl certificate, this will require some user input.
  echo "Setting up SSL certificates..."
  sudo certbot --nginx
fi

if ask_for_confirmation "Do you want to set up a cronjob to renew certificates?"; then
  echo "Setting up cron job to renew SSL certificates..."
  # update crontab with `0 5 1 * * sudo certbot renew --preferred-challenges http-01`
  cron_command="0 5 1 * * sudo certbot renew --preferred-challenges http-01"
  temp_cron_file=$(mktemp)
  echo "$cron_command" > "$temp_cron_file"
  crontab "$temp_cron_file"
  rm "$temp_cron_file"
else
  echo "Skipping cron job setup for SSL certificate renewal."
fi

print_status "SSL setup complete."
