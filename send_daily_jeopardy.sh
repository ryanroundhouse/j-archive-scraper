#!/bin/bash

# Daily Jeopardy Email Sender Script
# This script activates the virtual environment and sends the daily Jeopardy email

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate the virtual environment
source venv/bin/activate

# Run the daily Jeopardy email script
python daily_jeopardy_email.py

# Deactivate the virtual environment
deactivate

# Exit with the status of the Python script
exit $?

