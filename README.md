# Edge TTS for Claude

This project lets Claude speak using Microsoft Edge's high-quality text-to-speech voices in 30+ languages.

## Features

- Text-to-speech in multiple languages
- High-quality natural-sounding voices
- Simple integration with Claude

## Quick Start

1. Make sure you have Claude Desktop installed
2. Run the server with: `./start.sh`
3. Add the server to Claude's configuration file:

```json
{
  "mcpServers": {
    "edge-tts": {
      "command": "bash",
      "args": ["/full/path/to/edge-tts-mcp/start.sh"]
    }
  }
}
```

Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

4. Restart Claude

## Limitations

- Audio is limited to about 10 minutes per request
- The service uses an unofficial API to Microsoft Edge TTS

## Troubleshooting

If you encounter issues:

1. Check Claude's logs: `cat ~/Library/Logs/Claude/mcp.log`
2. Make sure the path to the start.sh script is correct in your configuration
3. Restart Claude after making any changes
