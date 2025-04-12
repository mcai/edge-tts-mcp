"""
This module provides a dictionary of recommended voices for different languages.
"""

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
