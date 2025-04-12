from mcp.server.fastmcp import FastMCP
import edge_tts
import tempfile
import os
from typing import List, Dict

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

def get_voice_for_language(language_code):
    """
    Get the recommended voice for a specific language code.
    
    Args:
        language_code: The language code (e.g., 'en-US', 'fr-FR')
        
    Returns:
        The recommended voice for the language or None if not found
    """
    return RECOMMENDED_VOICES.get(language_code)

def get_language_name(language_code):
    """
    Get the human-readable name of a language from its code.
    
    Args:
        language_code: The language code (e.g., 'en-US', 'fr-FR')
        
    Returns:
        The language name or the code itself if not found
    """
    return LANGUAGE_NAMES.get(language_code, language_code)

def list_supported_languages():
    """
    Return a list of all supported language codes.
    
    Returns:
        A list of language codes
    """
    return sorted(RECOMMENDED_VOICES.keys())

# Initialize the MCP server
mcp = FastMCP("Edge TTS Server")

# Text character limit for Edge TTS
MAX_CHARS = 64000  # ~64KB (2^16 = 65,536 bytes) with overhead for WebSocket message
# NOTE: The edge-tts library automatically handles chunking for large texts

@mcp.tool(description="Generate speech from text using Microsoft Edge TTS with support for 30+ languages (en-US, fr-FR, de-DE, es-ES, zh-CN, ja-JP, etc.) with automatic handling of texts up to 64KB")
async def text_to_speech(text: str, language: str = "en-US") -> str:
    """Generate speech from text using Microsoft Edge TTS.
    
    Args:
        text: The text to convert to speech (supports up to ~64,000 characters with automatic chunking)
        language: The language code to use (e.g., en-US, fr-FR, de-DE, es-ES, zh-CN, ja-JP)
               Available codes include: en-US (English), fr-FR (French), de-DE (German), 
               es-ES (Spanish), zh-CN (Chinese), ja-JP (Japanese), ru-RU (Russian),
               pt-BR (Portuguese), it-IT (Italian), nl-NL (Dutch), ar-SA (Arabic),
               and many more.
    
    Returns:
        Path to the generated audio file
    """
    # Get the recommended voice for the specified language
    voice = get_voice_for_language(language)
    
    # If language not found in our mapping, fall back to default
    if not voice:
        print(f"Warning: Language '{language}' not found. Using default voice.")
        voice = "en-US-GuyNeural"
    
    # Use default rate and volume
    rate = "+0%"
    volume = "+0%"
    
    print(f"Generating speech in {get_language_name(language)} with voice: {voice}")
    print(f"Text length: {len(text)} characters")
    
    # Note: edge-tts library automatically handles text chunking for large inputs
    # but we should still warn about potential audio length limits
    approx_words = len(text.split())
    # Average speaking rate is about 150 words per minute
    approx_minutes = approx_words / 150
    if approx_minutes > 10:
        print(f"Warning: Text may generate more than 10 minutes of audio (approximately {approx_minutes:.1f} minutes).")
        print("Audio output may be truncated after 10 minutes.")
    
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

@mcp.tool(description="Get list of supported languages for text-to-speech")
async def get_languages() -> List[Dict[str, str]]:
    """Get the list of supported languages for text-to-speech.
    
    Returns:
        List of dictionaries containing language code and name
    """
    try:
        supported_langs = list_supported_languages()
        result = []
        
        for lang_code in sorted(supported_langs):
            result.append({
                "code": lang_code,
                "name": get_language_name(lang_code)
            })
        
        print(f"Returning {len(result)} supported languages")
        return result
    except Exception as e:
        print(f"Error getting languages: {str(e)}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    print("Starting Edge TTS MCP Server...")
    print("Available tools:")
    print("- text_to_speech: Generate speech from text in different languages")
    print("- get_languages: Get list of supported languages")
    print("Limitations:")
    print("- The edge-tts library automatically handles chunking of large texts")
    print("- Maximum audio length per request: ~10 minutes")
    
    # Print a few example languages
    print("\nSupported languages include:")
    examples = ["en-US", "fr-FR", "de-DE", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
    for lang in examples:
        name = get_language_name(lang)
        print(f"- {lang} ({name})")
    print(f"...and {len(list_supported_languages()) - len(examples)} more.")
    
    print("\nServer is running. Press Ctrl+C to stop.")
    mcp.run()
