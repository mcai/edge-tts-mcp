#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

# Create Claude config directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude/

# Get the absolute path to the Python interpreter in the virtual environment
PYTHON_PATH="${SCRIPT_DIR}/venv/bin/python3"
SERVER_PATH="${SCRIPT_DIR}/edge_tts_server.py"

# Create the Claude configuration file
CONFIG_FILE=~/Library/Application\ Support/Claude/claude_desktop_config.json

# Create a new configuration file (overwrite existing)
echo '{
  "mcpServers": {
    "edgeTTS": {
      "command": "'"${PYTHON_PATH}"'",
      "args": ["'"${SERVER_PATH}"'"]
    }
  }
}' > "$CONFIG_FILE"

echo "Created configuration file with Edge TTS server."
echo "Python path: ${PYTHON_PATH}"
echo "Server path: ${SERVER_PATH}"
echo "Setup complete. Please restart Claude to apply the changes."
