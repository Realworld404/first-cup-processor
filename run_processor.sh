#!/bin/bash

# Wrapper script to load environment and run processor
# Used by Launch Agent to ensure .env is loaded

# Change to script directory
cd "$(dirname "$0")"

# Load environment variables from .env
if [ -f .env ]; then
    set -a  # Automatically export all variables
    source .env
    set +a
fi

# Run the processor with Anaconda Python
exec /Users/jasonbrett/anaconda3/bin/python3 youtube_processor.py
