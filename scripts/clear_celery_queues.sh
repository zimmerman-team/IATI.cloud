#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to clear the celery queue in the RabbitMQ docker container.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

print_status "Clearing celery queue in RabbitMQ docker container..."
sudo docker exec -it rabbitmq rabbitmqctl purge_queue celery
print_status "Done clearing celery queue in RabbitMQ docker container."
