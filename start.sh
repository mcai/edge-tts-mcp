#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Start the Edge TTS MCP server
echo "Starting Edge TTS MCP server..."
python3 edge_tts_server.py
