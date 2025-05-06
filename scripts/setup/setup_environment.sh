#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to set up the environment files for the IATI Cloud project.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Setup environment files
print_status "Preparing environment files."
cp ./.env.example.docker ./.env.dev
cp ./.env.example.docker ./.env.prod
cp ./.env.example.docker ./.env.staging
cp ./.env.example.docker ./.env.test

# Select the environment type to set up.
. ./scripts/select_env.sh

# Update the .env files with their correct values
print_status "Updating .env files with correct values. Please provide these required values:"
# Ask the user for their username and password
read -p "Enter your username: " username
read -sp "Enter your password. For Solr, Mongo and their connections, please omit any symbols such as @, # etcetera: " password
read -p "Enter your django superuser email: " email
read -p "Enter your IATI.cloud domain (ex.: localhost, datastore.iati.cloud):  " domain
read -p "Enter your trusted origin (ex.: https://datastore.iati.cloud): " trusted_origin
echo "Thank you for your input. The script will now proceed to update the .env files."
# Base64 encode the username and password for Solr
encoded_base64=$(echo -n "$username:$password" | base64)

# List of .env files
env_files=(.env.dev .env.test .env.staging .env.prod)
# Loop through each file and perform the replacement
for env_file in "${env_files[@]}"; do
  # Django secret key
  sed -i "s/SECRET_KEY=iati_cloud/SECRET_KEY=$password/g" "$env_file"
  # Postgres
  sed -i "s/POSTGRES_USER=iati_cloud/POSTGRES_USER=$username/g" "$env_file"
  sed -i "s/POSTGRES_PASSWORD=oipa/POSTGRES_PASSWORD=$password/g" "$env_file"
  # Solr
  sed -i "s/SOLR_ADMIN_USERNAME=admin_example/SOLR_ADMIN_USERNAME=$username/g" "$env_file"
  sed -i "s|SOLR_ADMIN_PASSWORD=exampl3_123!|SOLR_ADMIN_PASSWORD=$password|g" "$env_file"
  sed -i "s|SOLR_BASE_URL=http://admin_example:exampl3_123!@solr:8983/solr|SOLR_BASE_URL=http://$username:$password@solr:8983/solr|g" "$env_file"  # NOQA
  sed -i "s|SOLR_AUTH_ENCODED=YWRtaW5fZXhhbXBsZTpleGFtcGwzXzEyMyE=|SOLR_AUTH_ENCODED=$encoded_base64|g" "$env_file"
  # Flower
  sed -i "s/CELERYFLOWER_USER=zz/CELERYFLOWER_USER=$username/g" "$env_file"
  sed -i "s/CELERYFLOWER_PASSWORD=zz/CELERYFLOWER_PASSWORD=$password/g" "$env_file"
  # Django
  sed -i "s/DJANGO_SUPERUSER_USERNAME=admin_example/DJANGO_SUPERUSER_USERNAME=$username/g" "$env_file"
  sed -i "s|DJANGO_SUPERUSER_PASSWORD=exampl3_123!|DJANGO_SUPERUSER_PASSWORD=$password|g" "$env_file"
  sed -i "s|DJANGO_SUPERUSER_EMAIL=example@zimmerman.team|DJANGO_SUPERUSER_EMAIL=$email|g" "$env_file"
  # Mongo
  sed -i "s/MONGO_INITDB_ROOT_USERNAME=admin_example/MONGO_INITDB_ROOT_USERNAME=$username/g" "$env_file"
  sed -i "s|MONGO_INITDB_ROOT_PASSWORD=exampl3_123!|MONGO_INITDB_ROOT_PASSWORD=$password|g" "$env_file"
  sed -i "s|MONGO_CONNECTION_STRING=mongodb://admin_example:exampl3_123!@mongo:27017|MONGO_CONNECTION_STRING=mongodb://$username:$password@mongo:27017|g" "$env_file"  # NOQA
  # IC_DOMAIN and CSRF_TRUSTED_ORIGINS
  sed -i "s|IC_DOMAIN=localhost|IC_DOMAIN=$domain|g" "$env_file"
  sed -i "s|CSRF_TRUSTED_ORIGINS=https://<your_domain>|CSRF_TRUSTED_ORIGINS=$trusted_origin|g" "$env_file"
done

print_status "Done setting up the environment..."
