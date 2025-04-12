#!/bin/bash

# Simple wrapper script that delegates to the Python wrapper

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Make sure the wrapper is executable
chmod +x mcp_wrapper.py

# Run the Python wrapper
exec python3 mcp_wrapper.py
