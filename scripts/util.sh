#!/bin/bash

# Function to explain what a script is for, and how to use it.
helper() {
  # Expects 3 arguments:
  #   $1 the script name
  #   $2 the first argument of the original script
  #   $3 the help message
  if [ "$2" = "-h" ] || [ "$2" = "--help" ]; then
    echo "
======================================================
                     ${1##*/}
------------------------------------------------------
$3
======================================================
"
    exit 0
  fi
}

# Function to prompt user for Y/n choice
ask_for_confirmation() {
  # Expects one argument, the message to display
  echo ""
  echo ""
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

print_status() {
  # Expects one argument, the status message
  echo "

======================================================
                     Status Update
------------------------------------------------------
$1
======================================================
"
}
