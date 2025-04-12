# Edge TTS MCP Server

A high-performance Model Context Protocol (MCP) server that enables Claude to speak using Microsoft Edge's high-quality text-to-speech voices in 30+ languages.

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic that allows large language models like Claude to interact with external tools, APIs, and data sources. This server implements MCP to provide Claude with speech synthesis capabilities using Microsoft Edge's TTS service.

## Features

- **Text-to-Speech in 30+ Languages**: Supports multiple language varieties with natural-sounding voices
- **SSML Support**: Use Speech Synthesis Markup Language for advanced control over speech output
- **Voice Listing**: Dynamically retrieve all available voices from Microsoft's service
- **Performance Optimized**: 
  - Automatic text chunking for large inputs
  - Efficient memory management and resource cleanup
  - Structured logging and robust error handling

## Quick Start

### Prerequisites
- Claude Desktop application
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
    "edge-tts": {
      "command": "bash",
      "args": ["/full/path/to/edge-tts-mcp/start.sh"]
    }
  }
}
```

The configuration file is located at:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

2. Restart Claude Desktop

## Available MCP Tools

The server provides three MCP tools:

1. `text_to_speech` - Generate speech from text with customizable voice, rate, and volume
2. `list_voices` - Get a complete list of all available Microsoft Edge TTS voices
3. `play_with_ssml` - Use SSML markup for precise control over speech synthesis

## Usage Examples

### Basic Text-to-Speech

```python
# Convert text to speech with default English voice
await text_to_speech("Hello, this is a test message.")

# Use a different language
await text_to_speech("Bonjour, comment ça va?", "fr-FR-VivienneNeural")

# Adjust speech rate and volume
await text_to_speech("This is spoken slowly and louder.", "en-US-GuyNeural", "-20%", "+10%")
```

### Advanced SSML Usage

```python
# Use SSML for advanced control
ssml = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-AriaNeural">
    Normal speech. 
    <break time="500ms"/>
    <prosody rate="slow" pitch="+10%">
      This text is spoken slower and with higher pitch.
    </prosody>
  </voice>
</speak>
"""
await play_with_ssml(ssml)
```

## Supported Languages

The server supports over 30 languages including:

- English (US, UK, Australia, Canada, India)
- Spanish (Spain, Mexico)
- French, German, Italian, Portuguese
- Chinese (Simplified & Traditional), Japanese, Korean
- Russian, Arabic, Hindi, and many more

Each language has optimized neural voices that provide natural-sounding speech with proper pronunciation and intonation.

## Architecture

This server is built using:

- **FastMCP**: An optimized framework for building MCP servers
- **Edge TTS**: Microsoft's Edge Text-to-Speech engine
- **Pydantic**: For robust request validation and type safety
- **Asyncio**: For non-blocking I/O operations

## Technical Details

- **Text Processing**: Automatically chunks large texts for stable processing
- **Audio Format**: Generates MP3 files for high-quality audio playback
- **Performance**: Optimized for low latency and efficient memory usage
- **Logging**: Comprehensive logging with request IDs for easy debugging

## Limitations

- Audio is limited to about 10 minutes per request
- The service uses an unofficial API to Microsoft Edge TTS
- Some SSML features might have limited support
- The server requires internet access to fetch voice data from Microsoft

## Troubleshooting

If you encounter issues:

1. Check the server logs: `cat /tmp/edge_tts_mcp.log`
2. Check Claude's logs: `cat ~/Library/Logs/Claude/mcp.log`
3. Make sure the path to the start.sh script is correct in your configuration
4. Ensure you have the latest version of edge-tts installed: `pip install -U edge-tts`
5. Restart Claude after making any changes

## Further Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://support.anthropic.com/en/articles/10949351-getting-started-with-model-context-protocol-mcp-on-claude-for-desktop)
- [Microsoft Edge TTS Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)

## License

This project is open source and free to use.
