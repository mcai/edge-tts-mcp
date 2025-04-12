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

### Testing the Edge TTS

Before using with Claude, you can test that the TTS engine works:

```bash
./auto_test.sh
```

This will generate a test audio file and play it using the default voice.

### Starting the Server

Run the server with:

```bash
./start.sh
```

Keep this terminal window open while using Claude.

### Configuring Claude

The configuration for Claude has already been set up. If you need to reconfigure:

```bash
./setup_claude.sh
```

Then restart Claude.

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
2. Verify the server is running by executing `./start.sh` in a terminal
3. Ensure the virtual environment is being used (the scripts handle this automatically)
4. Test Edge TTS directly with `./auto_test.sh`
5. Restart Claude after making configuration changes

## Project Structure

```
~/Projects/edge-tts-mcp/
├── edge_tts_server.py   - Main MCP server script
├── requirements.txt     - Dependencies list
├── README.md           - Documentation
├── auto_test.sh        - Script to test TTS functionality
├── list_voices.py      - Script to list available voices
├── run_test.sh         - Interactive test script
├── setup_claude.sh     - Script to configure Claude
├── start.sh            - Script to start the server
├── test_edge_tts.py    - Interactive test script
└── venv/               - Python virtual environment
```

## License

MIT
