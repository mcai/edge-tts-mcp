# Edge TTS MCP Server for Claude

This project provides a Model Context Protocol (MCP) server that allows Claude to use Microsoft Edge's Text-to-Speech (TTS) capabilities on macOS.

## Features

- High-quality text-to-speech using Microsoft Edge voices
- Support for multiple voices and languages
- Adjustable speech rate and volume
- SSML support for advanced voice control
- Integration with Claude via MCP

## Installation

1. Clone or download this repository
2. Install the required dependencies using the included virtual environment:

```bash
# Setup is already done - dependencies are installed in the venv directory
```

## Usage

### Starting the Server

Run the server with:

```bash
./start.sh
```

Keep this terminal window open while using Claude.

### Configuring Claude

Add this Edge TTS server to Claude's configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "edge-tts": {
      "command": "bash",
      "args": ["FULL_PATH_TO_PROJECT/start.sh"]
    }
  }
}
```

Replace `FULL_PATH_TO_PROJECT` with the absolute path to the project directory (e.g., `/Users/username/Projects/edge-tts-mcp`). If the file already has other MCP servers, just add the "edge-tts" entry to the existing "mcpServers" object. Restart Claude after saving.

### Available Tools

The following tools are available through the MCP server:

- `text_to_speech`: Generate speech from text with adjustable parameters
- `list_voices`: List all available voices
- `play_with_ssml`: Play speech using SSML markup for advanced control

## Examples to Use in Claude

### Basic Text-to-Speech

```
Please read this text using Edge TTS: "Hello, I'm using Microsoft Edge TTS with Claude on macOS."
```

### Custom Voice and Settings

```
Please read this text using Edge TTS with voice en-GB-SoniaNeural, rate +10%, and volume +20%: "This is a test with adjusted parameters."
```

### Using SSML for Advanced Control

```
Please play this SSML using Edge TTS:
<speak>
  <voice name="en-US-AriaNeural">
    This is <emphasis level="strong">emphasized</emphasis> text.
    <break time="500ms"/>
    And this text comes after a pause.
  </voice>
</speak>
```

## Troubleshooting

If you encounter issues:

1. Check Claude's MCP logs: `cat ~/Library/Logs/Claude/mcp.log`
2. Make sure the path to the start.sh script in your Claude configuration is correct
3. Try running the start.sh script manually from the terminal to verify it works
4. Restart Claude after making configuration changes

## Project Structure

```
~/Projects/edge-tts-mcp/
├── edge_tts_server.py   - Main MCP server script
├── requirements.txt     - Dependencies list
├── README.md            - Documentation
├── start.sh             - Script to start the server
└── venv/                - Python virtual environment
```

## License

MIT
