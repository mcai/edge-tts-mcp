# English Podcast Conversation Server

A specialized Model Context Protocol (MCP) server for generating high-quality podcast conversations with alternating male and female voices using Microsoft Edge's text-to-speech technology.

## What is this?

This server makes it easy to create natural-sounding podcast conversations by alternating between professional male and female voices. It's designed specifically for podcast creators and content producers who want to quickly prototype or generate podcast-style content.

## Key Features

- **Simple Conversation Format**: Just specify speakers and text in a straightforward JSON structure
- **Professional Voices**: Uses high-quality neural voices from Microsoft Edge TTS
- **Easy Integration**: Works seamlessly with Claude and other MCP-compatible AI assistants
- **Optimized Performance**: Efficient generation and processing of multi-speaker audio
- **Single-Purpose Design**: Focused solely on podcast conversations for simplicity

## Quick Start

### Prerequisites
- macOS operating system
- Claude Desktop application (or another MCP client)
- Python 3.8 or higher
- Edge TTS library (`pip install edge-tts`)
- MCP library (`pip install mcp[cli]`)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/edge-tts-mcp.git
cd edge-tts-mcp
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Integrating with Claude Desktop

1. Add the server to Claude's configuration file:
```json
{
  "mcpServers": {
    "podcast-tts": {
      "command": "bash",
      "args": ["/full/path/to/edge-tts-mcp/start.sh"]
    }
  }
}
```

The configuration file is located at:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Restart Claude Desktop

## Usage

### Conversation Format

The server accepts a simple JSON format where each segment specifies a speaker and their text:

```json
[
  {
    "speaker": "male",
    "text": "Welcome to our podcast! I'm Alex, your host for today."
  },
  {
    "speaker": "female",
    "text": "And I'm Jordan. We have an exciting topic to discuss today."
  },
  {
    "speaker": "male",
    "text": "That's right! Today we're diving into the fascinating world of..."
  }
]
```

### Using from Claude

```
Can you create a podcast script about [topic] with two hosts, and then use the podcast-tts MCP server to generate audio for it?
```

## Voice Options

The server uses two dedicated podcast-quality voices:

- **Male Voice**: en-US-GuyNeural
- **Female Voice**: en-US-AriaNeural

These voices were chosen for their clarity, professional sound, and natural conversational quality.

## Technical Details

### Optional Parameters

- **rate**: Speaking rate adjustment (e.g., "+0%", "-10%", "+20%")
- **volume**: Volume adjustment (e.g., "+0%", "+10%", "-5%")

### Output

The server returns a JSON response with:

- Status (success/error)
- Number of segments processed
- Total word count
- Processing time
- Audio file path
- Detailed information about each segment

## Limitations

- Maximum conversation length: ~64KB total text
- Maximum audio length: ~10 minutes
- English language only
- Limited to two voice options (male/female)

## Troubleshooting

If you encounter issues:

1. Check the server logs: `cat /tmp/edge_tts_mcp.log`
2. Verify the server is running
3. Ensure your conversation format is correct (see example above)
4. Check that both "speaker" and "text" fields are present for each segment

## Further Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://support.anthropic.com/en/articles/10949351-getting-started-with-model-context-protocol-mcp-on-claude-for-desktop)
- [Microsoft Edge TTS Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

## License

This project is open source and free to use.
