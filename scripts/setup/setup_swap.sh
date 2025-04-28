#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to set up swap memory on the system.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Set up swap memory
print_status "Setting up swap memory..."
while true; do
    read -p "Enter the amount of swap memory in GB (default is 64, leave blank for default): " swap_size
    swap_size=${swap_size:-64}
    if [[ $swap_size =~ ^[1-9][0-9]*$ ]]; then
        print_status "Allocating ${swap_size}G of swap memory..."
        break
    else
        echo "Invalid input. Please enter a non-zero positive number."
    fi
done
sudo fallocate -l ${swap_size}G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

print_status "Swap memory setup complete."
