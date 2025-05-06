#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
    "$0
Used to run pytest with a coverage report over the direct_indexing module.

Usage:
    $0 [--help]

Options:
    -h [--help]     Show this help message and exit"

# Run pytest with coverage
print_status "Running tests with coverage..."
pytest --cov=direct_indexing --cov-report html:./coverage_report tests
print_status """Find the coverage report at:
$(pwd)/coverage_report/index.html"""
