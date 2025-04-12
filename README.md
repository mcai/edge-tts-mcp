# Edge TTS for Claude

This project lets Claude speak using Microsoft Edge's high-quality text-to-speech voices in 30+ languages.

## Features

- Text-to-speech in 30+ languages with natural-sounding voices
- Support for SSML (Speech Synthesis Markup Language) for advanced control
- Automatic text chunking for large inputs
- Comprehensive logging and error handling
- Voice listing capability to explore available options
- Fast and optimized speech generation

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

## Available Tools

The server provides three main tools:

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

## Limitations

- Audio is limited to about 10 minutes per request
- The service uses an unofficial API to Microsoft Edge TTS
- Some SSML features might have limited support

## Performance

The server includes several optimizations:
- Text chunking for large inputs to prevent timeouts
- Efficient memory usage for audio processing
- Structured logging for better debugging
- Improved error handling and recovery

## Troubleshooting

If you encounter issues:

1. Check the server logs: `cat /tmp/edge_tts_mcp.log`
2. Check Claude's logs: `cat ~/Library/Logs/Claude/mcp.log`
3. Make sure the path to the start.sh script is correct in your configuration
4. Ensure you have the latest version of edge-tts installed: `pip install -U edge-tts`
5. Restart Claude after making any changes

## License

This project is open source and free to use.
