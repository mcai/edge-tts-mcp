#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Start the Podcast TTS MCP server
echo "Starting Podcast TTS MCP server..."
python3 podcast_tts_mcp_server.py
