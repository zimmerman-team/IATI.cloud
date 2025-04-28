#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to restart IATI.cloud services (iaticloud, flower, workers, scheduler and revoke).

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Script to restart IATI.cloud services, and wait 15 seconds for all services to have started.
print_status "Restarting IATI.cloud (iaticloud, flower, workers, scheduler and revoke)"
echo "Shutting down"
sudo docker stop iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker celeryaidaworker
echo "Starting up..."
sudo docker compose up -d iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker celeryaidaworker
echo "..."
sleep 5
echo "..."
sleep 5
echo "..."
sleep 5
print_status "Done restarting."
