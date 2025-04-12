# Multilingual Podcast Conversation Server

A specialized Model Context Protocol (MCP) server for generating high-quality podcast conversations with alternating male and female voices using Microsoft Edge's text-to-speech technology. Supports English, Simplified Chinese, and Traditional Chinese.

## What is this?

This server makes it easy to create natural-sounding podcast conversations by alternating between professional male and female voices. It's designed specifically for podcast creators and content producers who want to quickly prototype or generate podcast-style content in multiple languages.

## Key Features

- **Multilingual Support**: Generate podcasts in English, Simplified Chinese, and Traditional Chinese
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
git clone https://github.com/mcai/podcast-tts-mcp.git
cd podcast-tts-mcp
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
      "args": ["/full/path/to/podcast-tts-mcp/start.sh"]
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
Can you create a podcast script about [topic] with two hosts, and then use the podcast-tts MCP server to generate audio for it in [language]?
```

## Voice Options

The server uses dedicated podcast-quality voices for each supported language:

### English (language code: "en")
- **Male Voice**: en-US-GuyNeural
- **Female Voice**: en-US-AriaNeural

### Simplified Chinese (language code: "zh-CN")
- **Male Voice**: zh-CN-YunyangNeural (professional and reliable, great for news reading)
- **Female Voice**: zh-CN-XiaoxiaoNeural (warm tone, suitable for news and novels)

### Traditional Chinese (language code: "zh-TW")
- **Male Voice**: zh-TW-YunJheNeural (friendly and positive, ideal for general content)
- **Female Voice**: zh-TW-HsiaoChenNeural (friendly and positive, suitable for general use)

These voices were chosen for their clarity, professional sound, and natural conversational quality.

## Technical Details

### Required Parameters

- **conversation**: Array of segments, each with "speaker" and "text" fields

### Optional Parameters

- **language**: Language code - "en" (default), "zh-CN", or "zh-TW"
- **rate**: Speaking rate adjustment (e.g., "+0%", "-10%", "+20%")
- **volume**: Volume adjustment (e.g., "+0%", "+10%", "-5%")

### Example with Language Selection

```json
{
  "conversation": [
    {"speaker": "male", "text": "欢迎收听我们的播客！我是今天的主持人Alex。"},
    {"speaker": "female", "text": "我是Jordan。今天我们有一个令人兴奋的话题要讨论。"}
  ],
  "language": "zh-CN",
  "rate": "+0%",
  "volume": "+5%"
}
```

### Output

The server returns a JSON response with:

- Status (success/error)
- Language used
- Number of segments processed
- Total word count
- Processing time
- Audio file path
- Detailed information about each segment

## Limitations

- Maximum conversation length: ~64KB total text
- Maximum audio length: ~10 minutes
- Limited to supported languages (English, Simplified Chinese, Traditional Chinese)
- Limited to two voice options per language (male/female)

## Troubleshooting

If you encounter issues:

1. Check the server logs: `cat /tmp/podcast_tts_debug.log`
2. Verify the server is running
3. Ensure your conversation format is correct (see examples above)
4. Check that both "speaker" and "text" fields are present for each segment
5. Verify you're using a supported language code ("en", "zh-CN", or "zh-TW")

## Further Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://support.anthropic.com/en/articles/10949351-getting-started-with-model-context-protocol-mcp-on-claude-for-desktop)
- [Microsoft Edge TTS Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

## License

This project is open source and free to use.
