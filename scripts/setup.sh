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
if ask_for_confirmation "Do you want to install Docker?"; then
  . ./scripts/setup/install_docker.sh
else
  echo "Skipping Docker installation."
fi

echo ""
echo ""
if ask_for_confirmation "Do you want to install NodeJS v16, npm and yarn?"; then
  . ./scripts/setup/install_node.sh
else
  echo "Skipping NodeJS, npm and yarn installation."
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
echo "Setup script is done, please set up your env, and run 'bash ./scripts/build.sh <MODE>' to build the project."
