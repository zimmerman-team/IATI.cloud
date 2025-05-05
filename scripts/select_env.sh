#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to select an environment for the application.
Symlinks the appropriate .env file to .env based on the user's choice.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Select and activate the desired environment.
print_status "Select the environment to enable."
echo "1) dev (default)"
echo "2) prod"
echo "3) staging"
echo "4) test"
read -p "Enter your choice [1-4]: " choice

case "$choice" in
    2) selected_env="prod" ;;
    3) selected_env="staging" ;;
    4) selected_env="test" ;;
    *) selected_env="dev" ;; # Default to dev
esac

ln -s .env.$selected_env .env

print_status "Symlinked .env.$selected_env to .env."
