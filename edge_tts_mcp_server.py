"""
English Podcast TTS Server

Microsoft Edge TTS integration for podcast content using the Model Context Protocol (MCP).
Specialized for multi-speaker podcast conversations with male and female voices.
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

# ======================= Podcast Voice Data =======================

# Dedicated voices for podcast TTS
PODCAST_VOICES = {
    "male": "en-US-GuyNeural",       # Male voice
    "female": "en-US-AriaNeural"     # Female voice
}

# ======================= Pydantic Models for Request Validation =======================

class ConversationSegment(BaseModel):
    """Pydantic model for a single conversation segment."""
    speaker: str = Field(..., description="Speaker gender ('male' or 'female')")
    text: str = Field(..., description="The text to be spoken by this speaker")
    
    @validator('speaker')
    def validate_speaker(cls, v):
        """Validate that the speaker is either 'male' or 'female'."""
        if v.lower() not in ["male", "female"]:
            raise ValueError("Speaker must be either 'male' or 'female'")
        return v.lower()
    
    @validator('text')
    def validate_text_not_empty(cls, v):
        """Validate text is not empty."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v

class PodcastConversation(BaseModel):
    """Pydantic model for a podcast conversation."""
    conversation: List[ConversationSegment] = Field(..., description="List of conversation segments")
    rate: str = Field("+0%", description="Speaking rate (e.g., -10%, +0%, +10%)")
    volume: str = Field("+0%", description="Volume adjustment (e.g., -10%, +0%, +10%)")
    
    @validator('conversation')
    def validate_conversation_not_empty(cls, v):
        """Validate that the conversation has at least one segment."""
        if not v:
            raise ValueError("Conversation cannot be empty")
        
        # Check total text length
        total_length = sum(len(segment.text) for segment in v)
        if total_length > 64000:
            raise ValueError(f"Total conversation length exceeds maximum (64000 chars). Got {total_length} chars.")
        
        return v
    
    @validator('rate', 'volume')
    def validate_percentage(cls, v):
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

# ======================= Helper Functions =======================

async def generate_speech(text: str, voice: str, rate: str, volume: str, output_file: str) -> None:
    """
    Generate speech for a text segment and save to a file.
    
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
mcp = FastMCP("English Podcast Conversation Server")

# Constants
TEMP_DIR = tempfile.gettempdir()

# ======================= MCP Tool =======================

@mcp.tool(description="Generate podcast conversation with alternating male and female voices.")
async def play_podcast(conversation: List[Dict[str, str]], rate: str = "+0%", volume: str = "+0%") -> str:
    """Generate a podcast conversation with alternating male and female speakers.

    Args:
        conversation: List of conversation segments, each with "speaker" (male/female) and "text" fields
        rate: Speaking rate (e.g., -10%, +0%, +10%)
        volume: Volume adjustment (e.g., -10%, +0%, +10%)
        
    Returns:
        Result of speech generation with audio file path
    """
    start_time = time.time()
    request_id = f"req_{int(start_time)}"
    
    try:
        # Validate inputs using Pydantic model
        # First convert the input to the expected format
        validated_segments = []
        for segment in conversation:
            # Handle potential casing differences
            speaker_key = next((k for k in segment.keys() if k.lower() == "speaker"), "speaker")
            text_key = next((k for k in segment.keys() if k.lower() == "text"), "text")
            
            if speaker_key in segment and text_key in segment:
                validated_segments.append(ConversationSegment(
                    speaker=segment[speaker_key],
                    text=segment[text_key]
                ))
                
        podcast_input = PodcastConversation(
            conversation=validated_segments,
            rate=rate,
            volume=volume
        )
        
        # Extract validated values
        segments = podcast_input.conversation
        rate = podcast_input.rate
        volume = podcast_input.volume
        
        # Log the request
        logger.info(f"[{request_id}] Podcast conversation request: {len(segments)} segments, "
                   f"rate={rate}, volume={volume}")
        
        # Create output file
        output_file = os.path.join(TEMP_DIR, f"podcast_conversation_{request_id}.mp3")
        
        # Process each segment
        temp_files = []
        segment_details = []
        
        for i, segment in enumerate(segments):
            # Get the voice based on speaker gender
            voice = PODCAST_VOICES[segment.speaker]
            
            # Create temporary file for this segment
            temp_output = os.path.join(TEMP_DIR, f"podcast_segment_{request_id}_{i}.mp3")
            
            try:
                # Generate speech for this segment
                logger.info(f"[{request_id}] Processing segment {i+1}/{len(segments)}: "
                           f"{segment.speaker} voice, {len(segment.text)} chars")
                
                await generate_speech(
                    text=segment.text,
                    voice=voice,
                    rate=rate,
                    volume=volume,
                    output_file=temp_output
                )
                
                temp_files.append(temp_output)
                
                # Save segment details for response
                segment_details.append({
                    "index": i,
                    "speaker": segment.speaker,
                    "voice": voice,
                    "text": segment.text,
                    "length": len(segment.text),
                    "word_count": len(segment.text.split())
                })
                
            except Exception as seg_error:
                logger.error(f"[{request_id}] Error processing segment {i+1}: {str(seg_error)}")
                # Continue with other segments even if one fails
        
        # Combine all audio files
        if len(temp_files) > 0:
            with open(output_file, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            # Play the combined file
            os.system(f"afplay {output_file}")
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"[{request_id}] Failed to remove temp file: {str(e)}")
        else:
            raise ValueError("No audio segments were successfully generated")
        
        # Log successful completion
        duration = time.time() - start_time
        logger.info(f"[{request_id}] Podcast conversation generated successfully in {duration:.2f}s")
        
        # Return successful response
        return json.dumps({
            "status": "success",
            "segments_processed": len(temp_files),
            "total_segments": len(segments),
            "segments": segment_details,
            "total_words": sum(segment["word_count"] for segment in segment_details),
            "audio_file": output_file,
            "processing_time": f"{duration:.2f}s"
        }, indent=2)
        
    except Exception as e:
        # Log error with traceback
        logger.error(f"[{request_id}] Error generating podcast conversation: {str(e)}", exc_info=True)
        
        # Return error information
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)

# ======================= Main Entry Point =======================

if __name__ == "__main__":
    server_start_time = time.time()
    
    print("╔══════════════════════════════════════════════════════╗")
    print("║     🎙️  English Podcast Conversation Server v1.0.0     ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    print("\n📋 Available tool:")
    print("   - play_podcast: Generate multi-speaker podcast conversations")
    
    print("\n📝 Input Format Example:")
    print("""   [
     {
         "speaker": "male",
         "text": "Welcome to our podcast! I'm Alex."
     },
     {
         "speaker": "female",
         "text": "And I'm Jordan. Today we'll be discussing..."
     },
     ...
   ]""")
    
    print("\n🎤 Dedicated podcast voices:")
    print(f"   - {PODCAST_VOICES['male']} (Male): Professional male voice")
    print(f"   - {PODCAST_VOICES['female']} (Female): Professional female voice")
    
    print(f"\n📁 Audio files saved to: {TEMP_DIR}")
    print(f"📝 Logs saved to: {os.path.join(TEMP_DIR, 'edge_tts_mcp.log')}")
    
    print("\n🚀 Server is running. Press Ctrl+C to stop.")
    
    # Add server startup to log
    logger.info(f"English Podcast Conversation Server v1.0.0 started")
    
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
