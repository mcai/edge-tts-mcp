from mcp.server.fastmcp import FastMCP
import edge_tts
import tempfile
import os
from typing import List

# Initialize the MCP server
mcp = FastMCP("Edge TTS Server")

@mcp.tool()
async def text_to_speech(text: str, voice: str = "en-US-GuyNeural", rate: str = "+0%", volume: str = "+0%") -> str:
    """Generate speech from text using Microsoft Edge TTS.
    
    Args:
        text: The text to convert to speech
        voice: The voice to use (e.g., en-US-SaraNeural)
        rate: Speaking rate (e.g., -10%, +0%, +10%)
        volume: Volume adjustment (e.g., -10%, +0%, +10%)
    
    Returns:
        Path to the generated audio file
    """
    print(f"Generating speech with voice: {voice}")
    print(f"Text: {text}")
    print(f"Rate: {rate}, Volume: {volume}")
    
    # Create a temporary file with mp3 extension
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, "edge_tts_output.mp3")
    
    # Configure Edge TTS
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume
    )
    
    # Generate speech and save to file
    try:
        await communicate.save(output_file)
        # Play the audio using macOS built-in afplay
        os.system(f"afplay {output_file}")
        return f"Speech generated successfully using voice {voice}"
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return f"Error generating speech: {str(e)}"

@mcp.tool()
async def list_voices() -> List[dict]:
    """List all available voices for Edge TTS."""
    try:
        voices = await edge_tts.VoicesManager.create()
        print(f"Found {len(voices.voices)} voices")
        return [
            {
                "voice": v["ShortName"], 
                "gender": v["Gender"],
                "locale": v["Locale"]
            } 
            for v in voices.voices
        ]
    except Exception as e:
        print(f"Error listing voices: {str(e)}")
        return [{"error": str(e)}]

@mcp.tool()
async def play_with_ssml(ssml: str, voice: str = "en-US-GuyNeural") -> str:
    """Generate speech using SSML markup for advanced control.
    
    Args:
        ssml: SSML markup text
        voice: The voice to use
        
    Returns:
        Result of speech generation
    """
    print(f"Generating speech with SSML and voice: {voice}")
    print(f"SSML: {ssml}")
    
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, "edge_tts_ssml_output.mp3")
    
    try:
        communicate = edge_tts.Communicate(
            text=ssml,
            voice=voice,
            is_ssml=True
        )
        
        await communicate.save(output_file)
        os.system(f"afplay {output_file}")
        return f"Speech with SSML generated successfully using voice {voice}"
    except Exception as e:
        print(f"Error generating speech with SSML: {str(e)}")
        return f"Error generating speech with SSML: {str(e)}"

if __name__ == "__main__":
    print("Starting Edge TTS MCP Server...")
    print("Available tools:")
    print("- text_to_speech: Generate speech from text")
    print("- list_voices: List all available voices")
    print("- play_with_ssml: Play speech using SSML markup")
    print("Server is running. Press Ctrl+C to stop.")
    mcp.run()
