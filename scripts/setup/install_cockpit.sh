#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to install cockpit, a web-based server management interface.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Install Cockpit
print_status "Installing Cockpit..."
sudo apt install cockpit -y
sudo systemctl enable --now cockpit.socket

print_status "Cockpit installed and enabled."
