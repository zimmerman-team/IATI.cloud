#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to set up the submodule (django static for the admin page)

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

print_status "Installing submodules..."
git submodule init
git submodule update

print_status "Copying the static files to '/static'..."
cp -r ./static /static

print_status "Submodules installed and static files copied."
