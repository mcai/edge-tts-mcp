#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Test the Edge TTS functionality non-interactively
echo "Testing Edge TTS functionality..."
python3 -c '
import asyncio
import edge_tts
import os

async def test():
    # Use a default voice and text
    voice = "en-US-GuyNeural"  # Different voice
    text = "This is a test of Microsoft Edge Text to Speech on macOS."
    
    print(f"Using voice: {voice}")
    print(f"Text: {text}")
    
    # Create a communication object
    communicate = edge_tts.Communicate(text=text, voice=voice)
    
    # Save to a file
    output_file = "test_output.mp3"
    await communicate.save(output_file)
    
    print(f"Speech saved to {output_file}")
    
    # Play the audio
    os.system(f"afplay {output_file}")
    
    print("Test complete!")

asyncio.run(test())
'
