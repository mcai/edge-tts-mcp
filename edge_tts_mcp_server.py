"""
Edge TTS MCP Server

Microsoft Edge TTS integration using the Model Context Protocol (MCP).
Provides high-quality text-to-speech in 30+ languages with optimized performance.
File: edge_tts_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
import edge_tts
import tempfile
import os
import asyncio
import logging
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(tempfile.gettempdir(), "edge_tts_mcp.log"))
    ]
)
logger = logging.getLogger("edge-tts-mcp")

# ======================= Voice and Language Data =======================

# Dictionary of recommended voices for different languages
RECOMMENDED_VOICES = {
    # English varieties
    "en-US": "en-US-AvaNeural",           # American English
    "en-GB": "en-GB-LibbyNeural",         # British English
    "en-AU": "en-AU-NatashaNeural",       # Australian English
    "en-CA": "en-CA-ClaraNeural",         # Canadian English
    "en-IN": "en-IN-NeerjaNeural",        # Indian English
    
    # Spanish varieties
    "es-ES": "es-ES-XimenaNeural",        # Spain Spanish
    "es-MX": "es-MX-DaliaNeural",         # Mexican Spanish
    
    # Other major European languages
    "fr-FR": "fr-FR-VivienneNeural",      # French
    "de-DE": "de-DE-SeraphinaNeural",     # German
    "it-IT": "it-IT-ElsaNeural",          # Italian
    "pt-BR": "pt-BR-ThalitaNeural",       # Brazilian Portuguese
    "ru-RU": "ru-RU-SvetlanaNeural",      # Russian
    "nl-NL": "nl-NL-ColetteNeural",       # Dutch
    "pl-PL": "pl-PL-ZofiaNeural",         # Polish
    "sv-SE": "sv-SE-SofieNeural",         # Swedish
    "tr-TR": "tr-TR-EmelNeural",          # Turkish
    
    # Asian languages
    "zh-CN": "zh-CN-XiaoxiaoNeural",      # Chinese (Mainland)
    "zh-TW": "zh-TW-HsiaoChenNeural",     # Chinese (Taiwan)
    "ja-JP": "ja-JP-NanamiNeural",        # Japanese
    "ko-KR": "ko-KR-SunHiNeural",         # Korean
    "hi-IN": "hi-IN-SwaraNeural",         # Hindi
    "ar-SA": "ar-SA-ZariyahNeural",       # Arabic
    "th-TH": "th-TH-AcharaNeural",        # Thai
    "vi-VN": "vi-VN-HoaiMyNeural",        # Vietnamese
    
    # Other languages
    "he-IL": "he-IL-HilaNeural",          # Hebrew
    "id-ID": "id-ID-GadisNeural",         # Indonesian
    "ms-MY": "ms-MY-YasminNeural",        # Malay
    "uk-UA": "uk-UA-PolinaNeural",        # Ukrainian
    "cs-CZ": "cs-CZ-VlastaNeural",        # Czech
    "hu-HU": "hu-HU-NoemiNeural",         # Hungarian
    "ro-RO": "ro-RO-AlinaNeural",         # Romanian
    "fi-FI": "fi-FI-SelmaNeural",         # Finnish
    "da-DK": "da-DK-ChristelNeural",      # Danish
    "no-NO": "nb-NO-IselinNeural",        # Norwegian
}

# Language name mapping for display purposes
LANGUAGE_NAMES = {
    "en-US": "English (US)",
    "en-GB": "English (UK)",
    "en-AU": "English (Australia)",
    "en-CA": "English (Canada)",
    "en-IN": "English (India)",
    "es-ES": "Spanish (Spain)",
    "es-MX": "Spanish (Mexico)",
    "fr-FR": "French",
    "de-DE": "German",
    "it-IT": "Italian",
    "pt-BR": "Portuguese (Brazil)",
    "ru-RU": "Russian",
    "nl-NL": "Dutch",
    "pl-PL": "Polish",
    "sv-SE": "Swedish",
    "tr-TR": "Turkish",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ja-JP": "Japanese",
    "ko-KR": "Korean",
    "hi-IN": "Hindi",
    "ar-SA": "Arabic",
    "th-TH": "Thai",
    "vi-VN": "Vietnamese",
    "he-IL": "Hebrew",
    "id-ID": "Indonesian",
    "ms-MY": "Malay",
    "uk-UA": "Ukrainian",
    "cs-CZ": "Czech",
    "hu-HU": "Hungarian",
    "ro-RO": "Romanian",
    "fi-FI": "Finnish",
    "da-DK": "Danish",
    "no-NO": "Norwegian",
}

# ======================= Pydantic Models for Request Validation =======================

class TTSInput(BaseModel):
    """Pydantic model for text-to-speech input validation."""
    text: str = Field(..., description="The text to convert to speech")
    voice: str = Field("en-US-GuyNeural", description="The voice to use (e.g., en-US-SaraNeural)")
    rate: str = Field("+0%", description="Speaking rate (e.g., -10%, +0%, +10%)")
    volume: str = Field("+0%", description="Volume adjustment (e.g., -10%, +0%, +10%)")
    
    @validator('text')
    def validate_text_length(cls, v):
        """Validate text length is within limits."""
        if len(v) <= 0:
            raise ValueError("Text cannot be empty")
        if len(v) > 64000:  # Max size for Edge TTS
            raise ValueError(f"Text exceeds maximum length of 64000 characters (got {len(v)})")
        return v
    
    @validator('rate', 'volume')
    def validate_percentage(cls, v, values, **kwargs):
        """Validate rate and volume follow the correct format."""
        if not (v.startswith('+') or v.startswith('-')) or not v.endswith('%'):
            raise ValueError(f"Must be in format +X% or -X% (e.g., +10%, -20%, +0%)")
        try:
            num = int(v[1:-1])
            if num < 0 or num > 100:
                raise ValueError(f"Percentage must be between 0 and 100")
        except ValueError:
            raise ValueError(f"Invalid percentage format: {v}")
        return v

class SSMLInput(BaseModel):
    """Pydantic model for SSML input validation."""
    ssml: str = Field(..., description="SSML markup text")
    voice: str = Field("en-US-GuyNeural", description="The voice to use")
    
    @validator('ssml')
    def validate_ssml(cls, v):
        """Validate SSML syntax."""
        if not v.startswith('<speak') or not v.endswith('</speak>'):
            raise ValueError("SSML must be enclosed in <speak> tags")
        return v

# ======================= Helper Functions =======================

def get_voice_for_language(language_code: str) -> Optional[str]:
    """
    Get the recommended voice for a specific language code.
    
    Args:
        language_code: The language code (e.g., 'en-US', 'fr-FR')
        
    Returns:
        The recommended voice for the language or None if not found
    """
    return RECOMMENDED_VOICES.get(language_code)

def get_language_name(language_code: str) -> str:
    """
    Get the human-readable name of a language from its code.
    
    Args:
        language_code: The language code (e.g., 'en-US', 'fr-FR')
        
    Returns:
        The language name or the code itself if not found
    """
    return LANGUAGE_NAMES.get(language_code, language_code)

def list_supported_languages() -> List[str]:
    """
    Return a list of all supported language codes.
    
    Returns:
        A list of language codes
    """
    return sorted(RECOMMENDED_VOICES.keys())

def chunk_text(text: str, max_length: int = 5000) -> List[str]:
    """
    Split text into chunks to handle large inputs efficiently.
    
    Args:
        text: The text to chunk
        max_length: Maximum size of each chunk (default: 5000 chars)
        
    Returns:
        List of text chunks
    """
    # Try to break at sentence boundaries when possible
    sentences = text.replace(". ", ".|").replace("? ", "?|").replace("! ", "!|").split("|")
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # If the sentence itself is too long, break it up
            if len(sentence) > max_length:
                words = sentence.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= max_length:
                        if current_chunk:
                            current_chunk += " " + word
                        else:
                            current_chunk = word
                    else:
                        chunks.append(current_chunk)
                        current_chunk = word
            else:
                current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

async def generate_speech(text: str, voice: str, rate: str, volume: str, output_file: str) -> None:
    """
    Generate speech for a text chunk and save to a file.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use
        rate: Speech rate
        volume: Volume adjustment
        output_file: Path to save the audio
        
    Returns:
        None
    
    Raises:
        Exception: If speech generation fails
    """
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume
        )
        
        await communicate.save(output_file)
    except Exception as e:
        logger.error(f"Speech generation error: {str(e)}")
        raise

# ======================= MCP Server Setup =======================

# Initialize the MCP server
mcp = FastMCP("Edge TTS MCP Server")

# Constants
MAX_CHARS = 64000  # ~64KB (2^16 = 65,536 bytes) with overhead for WebSocket message
DEFAULT_VOICE = "en-US-GuyNeural"
TEMP_DIR = tempfile.gettempdir()

# ======================= MCP Tools =======================

@mcp.tool(description="Generate speech from text using Microsoft Edge TTS.")
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
    start_time = time.time()
    request_id = f"req_{int(start_time)}"
    
    try:
        # Validate inputs using Pydantic model
        tts_input = TTSInput(text=text, voice=voice, rate=rate, volume=volume)
        
        # Extract validated values
        text = tts_input.text
        voice = tts_input.voice
        rate = tts_input.rate
        volume = tts_input.volume
        
        logger.info(f"[{request_id}] TTS request: voice={voice}, length={len(text)} chars")
        
        # Create a temporary file with mp3 extension
        output_file = os.path.join(TEMP_DIR, f"edge_tts_output_{request_id}.mp3")
        
        # For larger texts, use chunking for better stability
        if len(text) > 5000:
            logger.info(f"[{request_id}] Large text detected. Splitting into chunks.")
            chunks = chunk_text(text)
            logger.info(f"[{request_id}] Text split into {len(chunks)} chunks")
            
            temp_files = []
            for i, chunk in enumerate(chunks):
                temp_output = os.path.join(TEMP_DIR, f"edge_tts_chunk_{request_id}_{i}.mp3")
                await generate_speech(chunk, voice, rate, volume, temp_output)
                temp_files.append(temp_output)
            
            # Concatenate audio files if multiple chunks
            # Note: This is a simple concatenation which might cause slight discontinuities
            # A more advanced approach would be to use ffmpeg or similar for seamless joining
            if len(temp_files) > 1:
                with open(output_file, 'wb') as outfile:
                    for temp_file in temp_files:
                        with open(temp_file, 'rb') as infile:
                            outfile.write(infile.read())
                
                # Clean up temporary chunk files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.warning(f"[{request_id}] Failed to remove temp file {temp_file}: {str(e)}")
            else:
                # If there's only one chunk, just rename it
                os.rename(temp_files[0], output_file)
        else:
            # For smaller texts, process directly
            await generate_speech(text, voice, rate, volume, output_file)
        
        # Play the audio using macOS built-in afplay
        os.system(f"afplay {output_file}")
        
        # Log successful completion
        duration = time.time() - start_time
        logger.info(f"[{request_id}] Speech generated successfully in {duration:.2f}s using voice {voice}")
        
        return json.dumps({
            "status": "success",
            "voice": voice,
            "text_length": len(text),
            "audio_file": output_file,
            "processing_time": f"{duration:.2f}s"
        })
        
    except Exception as e:
        # Log error with traceback
        logger.error(f"[{request_id}] Error generating speech: {str(e)}", exc_info=True)
        
        # Return error information
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })

@mcp.tool(description="List all available voices for Edge TTS.")
async def list_voices() -> List[Dict[str, str]]:
    """List all available voices for Edge TTS.
    
    Returns:
        List of available voices with their details
    """
    try:
        # This makes a network request to fetch voices from Microsoft
        voices = await edge_tts.VoicesManager.create()
        voice_list = voices.voices
        
        # Log the successful voice fetch
        logger.info(f"Successfully fetched {len(voice_list)} voices from Microsoft Edge TTS")
        
        # Return the list of voices
        return voice_list
    except Exception as e:
        logger.error(f"Error listing voices: {str(e)}", exc_info=True)
        return [{"error": str(e)}]

@mcp.tool(description="Generate speech using SSML markup for advanced control.")
async def play_with_ssml(ssml: str, voice: str = "en-US-GuyNeural") -> str:
    """Generate speech using SSML markup for advanced control.

    Args:
        ssml: SSML markup text
        voice: The voice to use
        
    Returns:
        Result of speech generation
    """
    start_time = time.time()
    request_id = f"req_{int(start_time)}"
    
    try:
        # Validate inputs
        ssml_input = SSMLInput(ssml=ssml, voice=voice)
        
        logger.info(f"[{request_id}] SSML request: voice={voice}, length={len(ssml)} chars")
        
        # Create output file
        output_file = os.path.join(TEMP_DIR, f"edge_tts_ssml_{request_id}.mp3")
        
        # Generate speech with SSML
        communicate = edge_tts.Communicate(
            ssml=ssml_input.ssml,
            voice=ssml_input.voice
        )
        
        await communicate.save(output_file)
        
        # Play the audio
        os.system(f"afplay {output_file}")
        
        # Log success
        duration = time.time() - start_time
        logger.info(f"[{request_id}] SSML speech generated successfully in {duration:.2f}s using voice {voice}")
        
        return json.dumps({
            "status": "success",
            "voice": voice,
            "ssml_length": len(ssml),
            "audio_file": output_file,
            "processing_time": f"{duration:.2f}s"
        })
        
    except Exception as e:
        logger.error(f"[{request_id}] Error generating SSML speech: {str(e)}", exc_info=True)
        
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })

# ======================= Main Entry Point =======================

if __name__ == "__main__":
    server_start_time = time.time()
    
    print("╔════════════════════════════════════════╗")
    print("║     🔊 Edge TTS MCP Server v1.1.0      ║")
    print("╚════════════════════════════════════════╝")
    
    print("\n📋 Available tools:")
    print("   - text_to_speech: Generate speech from text")
    print("   - list_voices: List all available voices from Microsoft")
    print("   - play_with_ssml: Use SSML for advanced control")
    
    print("\n⚠️ Limitations:")
    print("   - Max text length: ~64KB (chunked automatically)")
    print("   - Max audio length: ~10 minutes per request")
    
    # Print a few example languages
    print("\n🌍 Supported languages include:")
    examples = ["en-US", "fr-FR", "de-DE", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
    for lang in examples:
        name = get_language_name(lang)
        print(f"   - {lang} ({name})")
    print(f"   ...and {len(list_supported_languages()) - len(examples)} more.")
    
    print(f"\n📁 Audio files saved to: {TEMP_DIR}")
    print(f"📝 Logs saved to: {os.path.join(TEMP_DIR, 'edge_tts_mcp.log')}")
    
    print("\n🚀 Server is running. Press Ctrl+C to stop.")
    
    # Add server startup to log
    logger.info(f"Edge TTS MCP Server v1.1.0 started")
    
    try:
        # Run the MCP server
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        logger.info("Server shutdown requested by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Server error: {str(e)}", exc_info=True)
    finally:
        server_uptime = time.time() - server_start_time
        logger.info(f"Server shutdown. Uptime: {server_uptime:.2f} seconds")
        print("✓ Shutdown complete.")
