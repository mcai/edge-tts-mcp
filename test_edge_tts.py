#!/usr/bin/env python3
"""
Simple script to test Edge TTS functionality without the MCP server.
This helps verify that the TTS engine works properly on your system.
"""

import asyncio
import edge_tts
import os
import sys

async def test_edge_tts():
    text = "This is a test of Microsoft Edge Text to Speech on macOS."
    
    try:
        # Get the list of available voices
        print("Fetching available voices...")
        voices = await edge_tts.VoicesManager.create()
        
        # Print some voice options
        print("\nSome available voices:")
        for i, voice in enumerate(voices.voices[:5]):
            print(f"{i+1}. {voice['ShortName']} - {voice['Gender']} - {voice['Locale']}")
        
        # Use a default voice
        voice = "en-US-SaraNeural"
        
        # Ask user if they want to choose a voice
        choice = input(f"\nUse default voice '{voice}'? (y/n): ")
        if choice.lower() == 'n':
            choice = input("Enter a voice (e.g., en-US-GuyNeural): ")
            if choice:
                voice = choice
        
        print(f"\nGenerating speech with voice: {voice}")
        print(f"Text: \"{text}\"")
        
        # Generate speech
        communicate = edge_tts.Communicate(text=text, voice=voice)
        
        # Save to a file
        output_file = "test_output.mp3"
        await communicate.save(output_file)
        
        print(f"\nSpeech saved to {output_file}")
        
        # Play the audio on macOS
        print("Playing audio...")
        os.system(f"afplay {output_file}")
        
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_edge_tts())
    sys.exit(exit_code)
