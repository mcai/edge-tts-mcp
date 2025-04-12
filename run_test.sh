#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the test script
python3 test_edge_tts.py
