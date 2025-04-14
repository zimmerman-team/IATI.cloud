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

print_status "Installing submodules..."
git submodule init
git submodule update

print_status "Preparing environment files."
# cp ./monitoring/.env.example ./monitoring/.env
cp ./.env.example.docker ./.env.dev
cp ./.env.example.docker ./.env.prod
cp ./.env.example.docker ./.env.staging
cp ./.env.example.docker ./.env.test
ln -s ./.env.prod ./.env

# update the .env files with their correct values

print_status "Updating .env files with correct values. Please provide these required values:"
# Ask the user for their username and password
read -p "Enter your username: " username
read -sp "Enter your password: " password
read -p "Enter your django superuser email: " email
read -p "Enter your IATI.cloud domain (ex.: localhost, datastore.iati.cloud):  " domain
read -p "Enter your trusted origin (ex.: https://datastore.iati.cloud): " trusted_origin
echo ""
# password encoded:
encoded_base64=$(echo -n "$username:$password" | base64)

# List of .env files
env_files=(.env.dev .env.test .env.staging .env.prod)
# Loop through each file and perform the replacement
for env_file in "${env_files[@]}"; do
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

print_status "Done... (By default, .env has been symlinked to .env.prod.)"

echo ""
echo ""
if ask_for_confirmation "Do you want to set up a mounted solr directory?"; then
  df -h
  read -p "Enter your mounted directory: " mounted_dir
  sudo mkdir -p $mounted_dir/solr_data
  sudo chown -R 1001:root $mounted_dir/solr_data/
  # replace the string "solr_data:/bitnami" in docker-compose.yml
  sed -i "s|solr_data:/bitnami|$mounted_dir/solr_data:/bitnami|g" docker-compose.yml
else
  echo "Skipping mounted solr directory."
fi

print_status "Copying the static files..."
cp -r ./static /static
