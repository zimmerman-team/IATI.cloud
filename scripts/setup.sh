#!/bin/bash

# Help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Used to set up the repository. Specify the environment type."
  echo "Optionally initialises git submodules and their setups."
  echo "Removes any .env file, and creates a copy of .env.example with the appropriate name, then symlinks it to .env."
  echo "Optionally prepopulates DX with data"
  echo ""
  echo "Usage: . $0"
  exit 0
fi

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

echo ""
echo ""
if ask_for_confirmation "Do you want to setup additional swap memory (recommended, requires 64GB free space)?"; then
  sudo fallocate -l 64G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  sudo echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
else
  echo "Skipping Docker installation."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to install Docker?"; then
  . ./scripts/setup/install_docker.sh
else
  echo "Skipping Docker installation."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to initialise the submodules?"; then
  . ./scripts/setup/install_submodules.sh
else
  echo "Skipping the submodules."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to set up the query builder?"; then
  . ./scripts/setup/setup_iati_cloud_frontend.sh
else
  echo "Skipping the Query Builder."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to install NGINX with SSL enabled?"; then
  . ./scripts/setup/install_nginx.sh
else
  echo "Skipping NGINX."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to set up Solr (must be done before stack can be activated)?"; then
  . ./scripts/setup/setup_solr.sh
else
  echo "Skipping Solr."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to set up the IATI.cloud docker image? If you choose the Y option, there will be a manual step: hit control+c when the image is fully built and running."; then
  sudo docker compose up iaticloud
else
  echo "Setup script is done, please set up your env, and run 'bash ./scripts/build.sh <MODE>' to build the project."
fi

echo "Setup script is done. Start iati.cloud using the './scripts/start.sh <MODE>' script, or simply with: 'sudo docker compose up -d'."
