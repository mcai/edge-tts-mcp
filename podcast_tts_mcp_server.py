"""
English Podcast TTS Server

Microsoft Edge TTS integration for podcast content using the Model Context Protocol (MCP).
Specialized for multi-speaker podcast conversations with male and female voices.
"""

# ======================= Imports =======================
from fastmcp import FastMCP, Context
import edge_tts
import tempfile
import os
import sys
import json
import time
import asyncio
import subprocess
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

# ======================= Configure Logging =======================
# Set up logging to stderr to avoid interfering with MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("podcast-tts-mcp")

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
    
    @field_validator('speaker')
    @classmethod
    def validate_speaker(cls, v):
        """Validate that the speaker is either 'male' or 'female'."""
        if v.lower() not in ["male", "female"]:
            raise ValueError("Speaker must be either 'male' or 'female'")
        return v.lower()
    
    @field_validator('text')
    @classmethod
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
    
    @field_validator('conversation')
    @classmethod
    def validate_conversation_not_empty(cls, v):
        """Validate that the conversation has at least one segment."""
        if not v:
            raise ValueError("Conversation cannot be empty")
        
        # Check total text length
        total_length = sum(len(segment.text) for segment in v)
        if total_length > 64000:
            raise ValueError(f"Total conversation length exceeds maximum (64000 chars). Got {total_length} chars.")
        
        return v
    
    @field_validator('rate', 'volume')
    @classmethod
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

# ======================= Constants =======================
TEMP_DIR = tempfile.gettempdir()
REQUEST_EXPIRY_SECONDS = 3600  # Requests expire after 1 hour to prevent memory leaks

# ======================= Request Storage =======================
PODCAST_REQUESTS = {}  # Dictionary to store request statuses and information
REQUEST_LOCK = asyncio.Lock()  # Lock to prevent race conditions when updating requests

# ======================= Helper Functions =======================

def log_info(msg):
    """Log info to stderr to avoid disrupting MCP protocol."""
    logger.info(msg)
    print(f"INFO: {msg}", file=sys.stderr)

def log_error(msg):
    """Log error to stderr to avoid disrupting MCP protocol."""
    logger.error(msg)
    print(f"ERROR: {msg}", file=sys.stderr)

def log_debug(msg):
    """Log debug info to stderr to avoid disrupting MCP protocol."""
    logger.debug(msg)
    print(f"DEBUG: {msg}", file=sys.stderr)

def log_warning(msg):
    """Log warning to stderr to avoid disrupting MCP protocol."""
    logger.warning(msg)
    print(f"WARNING: {msg}", file=sys.stderr)

async def generate_speech(text: str, voice: str, rate: str, volume: str, output_file: str, ctx: Context = None) -> None:
    """
    Generate speech for a text segment and save to a file.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use
        rate: Speech rate
        volume: Volume adjustment
        output_file: Path to save the audio
        ctx: MCP context for logging (optional)
        
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
        
        if ctx:
            await ctx.debug(f"Generating speech with voice {voice}, rate {rate}, volume {volume}")
        
        await communicate.save(output_file)
        
        if ctx:
            await ctx.debug(f"Speech saved to {output_file}")
    except Exception as e:
        if ctx:
            await ctx.error(f"Speech generation error: {str(e)}")
        raise

async def cleanup_old_requests():
    """Periodically clean up old requests to prevent memory leaks."""
    log_info("Starting request cleanup background task")
    
    while True:
        try:
            current_time = time.time()
            requests_to_remove = []
            
            async with REQUEST_LOCK:
                for req_id, req_data in PODCAST_REQUESTS.items():
                    # Check if request is older than the expiry time
                    if current_time - req_data.get("submitted_at", current_time) > REQUEST_EXPIRY_SECONDS:
                        requests_to_remove.append(req_id)
                
                # Remove expired requests
                if requests_to_remove:
                    log_info(f"Cleaning up {len(requests_to_remove)} expired podcast requests")
                    for req_id in requests_to_remove:
                        del PODCAST_REQUESTS[req_id]
            
            # Sleep for a while before checking again
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            # Log the error but ensure the cleanup task doesn't crash
            log_error(f"Error in cleanup task: {e}")
            await asyncio.sleep(300)

async def process_podcast_request(request_id: str, segments: List[ConversationSegment], 
                               rate: str, volume: str, ctx: Optional[Context] = None) -> Dict:
    """
    Process a podcast TTS request asynchronously.
    
    Args:
        request_id: Unique ID for the request
        segments: List of validated ConversationSegment objects
        rate: Speaking rate adjustment
        volume: Volume adjustment
        ctx: MCP context for logging
        
    Returns:
        Dict with processing results
    """
    try:
        start_time = time.time()
        
        # Update request status
        async with REQUEST_LOCK:
            PODCAST_REQUESTS[request_id]["status"] = "processing"
            PODCAST_REQUESTS[request_id]["progress"] = 0
            PODCAST_REQUESTS[request_id]["total_segments"] = len(segments)
        
        # Create output file
        output_file = os.path.join(TEMP_DIR, f"podcast_conversation_{request_id}.mp3")
        
        # Process each segment
        temp_files = []
        segment_details = []
        
        total_segments = len(segments)
        if ctx:
            await ctx.info(f"Beginning speech generation for {total_segments} segments")
        
        for i, segment in enumerate(segments):
            # Report progress
            if ctx:
                await ctx.report_progress(i, total_segments)
                
            # Update progress in request storage
            async with REQUEST_LOCK:
                PODCAST_REQUESTS[request_id]["progress"] = i
                
            # Get the voice based on speaker gender
            voice = PODCAST_VOICES[segment.speaker]
            
            # Create temporary file for this segment
            temp_output = os.path.join(TEMP_DIR, f"podcast_segment_{request_id}_{i}.mp3")
            
            if ctx:
                await ctx.info(f"Processing segment {i+1}/{total_segments}: {segment.speaker} voice, {len(segment.text)} chars")
            
            try:
                # Generate speech for this segment
                await generate_speech(
                    text=segment.text,
                    voice=voice,
                    rate=rate,
                    volume=volume,
                    output_file=temp_output,
                    ctx=ctx
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
                
                if ctx:
                    await ctx.debug(f"Segment {i+1} processed successfully")
                
            except Exception as seg_error:
                if ctx:
                    await ctx.error(f"Error processing segment {i+1}: {str(seg_error)}")
                
                # Update request status with error
                async with REQUEST_LOCK:
                    PODCAST_REQUESTS[request_id]["errors"].append({
                        "segment": i,
                        "error": str(seg_error)
                    })
                # Continue with other segments even if one fails
        
        # Combine all audio files
        result = {}
        
        if len(temp_files) > 0:
            if ctx:
                await ctx.info(f"Combining {len(temp_files)} audio segments into final file")
                
            with open(output_file, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            # Play the combined file in a non-blocking way
            if ctx:
                await ctx.info(f"Playing audio file: {output_file}")
            
            # Use subprocess with Popen instead of os.system to avoid blocking
            try:
                # Start the audio playback in a separate process
                proc = subprocess.Popen(["afplay", output_file], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
                
                log_info(f"Started audio playback in background process (PID: {proc.pid})")
                
                if ctx:
                    await ctx.debug("Audio playback started in background process")
            except Exception as play_error:
                if ctx:
                    await ctx.warning(f"Audio playback error: {str(play_error)}")
            
            # Clean up temporary files
            if ctx:
                await ctx.debug("Cleaning up temporary files")
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception as e:
                    if ctx:
                        await ctx.warning(f"Failed to remove temp file {temp_file}: {str(e)}")
            
            # Calculate duration
            duration = time.time() - start_time
            
            if ctx:
                await ctx.info(f"Podcast generation completed in {duration:.2f} seconds")
                await ctx.report_progress(total_segments, total_segments)  # Mark as complete
            
            # Prepare result
            result = {
                "status": "success",
                "segments_processed": len(temp_files),
                "total_segments": len(segments),
                "segments": segment_details,
                "total_words": sum(segment["word_count"] for segment in segment_details),
                "audio_file": output_file,
                "processing_time": f"{duration:.2f}s"
            }
        else:
            error_msg = "No audio segments were successfully generated"
            if ctx:
                await ctx.error(error_msg)
            
            result = {
                "status": "error",
                "error": error_msg,
                "error_type": "ProcessingError"
            }
        
        # Update request status
        async with REQUEST_LOCK:
            if result.get("status") == "success":
                PODCAST_REQUESTS[request_id]["status"] = "completed"
                PODCAST_REQUESTS[request_id]["result"] = result
                PODCAST_REQUESTS[request_id]["progress"] = total_segments
            else:
                PODCAST_REQUESTS[request_id]["status"] = "failed"
                PODCAST_REQUESTS[request_id]["result"] = result
        
        return result
            
    except Exception as e:
        # Log error
        if ctx:
            await ctx.error(f"Error generating podcast conversation: {str(e)}")
        
        # Update request status
        async with REQUEST_LOCK:
            PODCAST_REQUESTS[request_id]["status"] = "failed"
            PODCAST_REQUESTS[request_id]["result"] = {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
        
        # Return error information
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

# ======================= Lifespan Context Manager =======================
@asynccontextmanager
async def server_lifespan(app):
    """Server lifespan context manager that handles startup and shutdown tasks."""
    log_info("Server starting up - initializing background tasks")
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_requests())
    
    # Yield control back to the server
    try:
        yield
    finally:
        # Clean up on shutdown
        log_info("Server shutting down - cleaning up tasks")
        if not cleanup_task.done():
            cleanup_task.cancel()
        log_info("Server shutdown complete")

# ======================= Initialize the MCP Server =======================
# Initialize the FastMCP server with lifespan management
mcp = FastMCP(
    "English Podcast Conversation Server",
    debug_logs=False,
    lifespan=server_lifespan
)

log_info("MCP server initialized")

# ======================= MCP Tools =======================

@mcp.tool(description="""Submit a podcast TTS request with alternating male and female voices.

Expected Arguments:
- conversation (required): List of dictionaries, each containing:
  * "speaker": Must be either "male" or "female" (case-insensitive)
  * "text": The content to be spoken (cannot be empty)
  * Example: [{"speaker": "male", "text": "Hello!"}, {"speaker": "female", "text": "Hi there!"}]
  * The total text length across all segments must not exceed 64,000 characters

- rate (optional): Speaking rate adjustment in format "+X%" or "-X%" 
  * Default: "+0%" (normal speed)
  * Examples: "+10%" (faster), "-20%" (slower)
  * Percentage must be between 0-100

- volume (optional): Volume adjustment in format "+X%" or "-X%"
  * Default: "+0%" (normal volume)
  * Examples: "+10%" (louder), "-5%" (quieter)
  * Percentage must be between 0-100
""")
async def play_podcast(conversation: List[Dict[str, str]], rate: str = "+0%", volume: str = "+0%", ctx: Context = None) -> str:
    """Submit a podcast TTS request and start playing the audio when ready.

    Args:
        conversation: List of conversation segments, each with "speaker" (male/female) and "text" fields.
                     Each segment must be a dictionary with keys:
                     - "speaker": Must be "male" or "female" (case-insensitive)
                     - "text": The content to be spoken (cannot be empty)
                     Example: [{"speaker": "male", "text": "Hello!"}, {"speaker": "female", "text": "Hi there!"}]
        rate: Speaking rate adjustment in format "+X%" or "-X%". Default: "+0%".
              Examples: "+10%" (faster), "-20%" (slower). Percentage must be between 0-100.
        volume: Volume adjustment in format "+X%" or "-X%". Default: "+0%".
                Examples: "+10%" (louder), "-5%" (quieter). Percentage must be between 0-100.
        
    Returns:
        JSON string with the following fields:
        - request_id: Unique ID for this request
        - status: "submitted" (initially)
        - message: Confirmation message
        
        In case of error:
        - status: "error"
        - error: Error message
        - error_type: Name of the exception type
    """
    try:
        # Generate a unique request ID
        request_id = f"req_{int(time.time())}"
        
        # Log request start
        if ctx:
            await ctx.info(f"Starting podcast conversation generation with {len(conversation)} segments")
            await ctx.info(f"Settings: rate={rate}, volume={volume}, request_id={request_id}")
        
        log_info(f"Received podcast request: {request_id} with {len(conversation)} segments")
            
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
        
        if ctx:
            await ctx.info(f"Validated {len(validated_segments)} conversation segments")
        
        # Extract validated values
        segments = podcast_input.conversation
        rate = podcast_input.rate
        volume = podcast_input.volume
        
        # Store request in global storage
        async with REQUEST_LOCK:
            PODCAST_REQUESTS[request_id] = {
                "status": "submitted",
                "submitted_at": time.time(),
                "progress": 0,
                "total_segments": len(segments),
                "errors": [],
                "settings": {
                    "rate": rate,
                    "volume": volume,
                },
                "result": None
            }
        
        # Start processing in background
        # We no longer need to register the task as lifespan handles task management
        asyncio.create_task(process_podcast_request(
            request_id=request_id,
            segments=segments,
            rate=rate,
            volume=volume,
            ctx=ctx
        ))
        
        log_info(f"Started background processing for request: {request_id}")
        
        # Return request info immediately
        return json.dumps({
            "status": "submitted",
            "request_id": request_id,
            "message": f"Podcast TTS request submitted with {len(segments)} segments. Use check_podcast_status to monitor progress.",
            "total_segments": len(segments)
        }, indent=2)
        
    except Exception as e:
        # Log error
        log_error(f"Error submitting podcast request: {str(e)}")
        if ctx:
            await ctx.error(f"Error submitting podcast conversation: {str(e)}")
            
        # Return error information
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)


@mcp.tool(description="""Check the status of a previously submitted podcast TTS request.

Expected Arguments:
- request_id (required): The request ID returned when submitting the podcast TTS request
  * Example: "req_1649875030"
""")
async def check_podcast_status(request_id: str, ctx: Context = None) -> str:
    """Check the status of a previously submitted podcast TTS request.

    Args:
        request_id: The unique identifier for the podcast TTS request (returned when submitting)
        
    Returns:
        JSON string with the status information:
        - status: "submitted", "processing", "completed", "failed", or "not_found"
        - progress: Number of segments processed so far
        - total_segments: Total number of segments in the conversation
        - progress_percentage: Percentage of processing completed
        - submitted_at: Timestamp when the request was submitted
        - ... and other information based on the status
        
        If status is "completed", includes the full result information.
        If status is "failed", includes error information.
    """
    try:
        if ctx:
            await ctx.info(f"Checking status for podcast TTS request: {request_id}")
        
        log_info(f"Checking status for request: {request_id}")
        
        # Check if request exists
        async with REQUEST_LOCK:
            if request_id not in PODCAST_REQUESTS:
                log_info(f"Request not found: {request_id}")
                return json.dumps({
                    "status": "not_found",
                    "message": f"No podcast TTS request found with ID: {request_id}"
                }, indent=2)
            
            # Get request data
            request_data = PODCAST_REQUESTS[request_id]
            
            # Calculate progress percentage
            if request_data["total_segments"] > 0:
                progress_percentage = round((request_data["progress"] / request_data["total_segments"]) * 100, 1)
            else:
                progress_percentage = 0
            
            # Prepare response based on status
            response = {
                "status": request_data["status"],
                "request_id": request_id,
                "progress": request_data["progress"],
                "total_segments": request_data["total_segments"],
                "progress_percentage": progress_percentage,
                "submitted_at": request_data["submitted_at"],
                "submitted_at_formatted": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(request_data["submitted_at"]))
            }
            
            # Add additional data based on status
            if request_data["status"] == "completed" and request_data["result"]:
                response.update(request_data["result"])
                
                # Just include the audio file info without playing it
                if request_data["result"].get("status") == "success" and "audio_file" in request_data["result"]:
                    if ctx:
                        await ctx.info(f"TTS request completed: {request_data['result']['audio_file']}")
                    
            elif request_data["status"] == "failed" and request_data["result"]:
                response.update(request_data["result"])
            
            # Include any errors
            if request_data["errors"]:
                response["errors"] = request_data["errors"]
        
        log_info(f"Status for request {request_id}: {request_data['status']}")
        if ctx:
            await ctx.info(f"Status for request {request_id}: {request_data['status']}")
            
        return json.dumps(response, indent=2)
        
    except Exception as e:
        # Log error
        log_error(f"Error checking podcast status: {str(e)}")
        if ctx:
            await ctx.error(f"Error checking podcast status: {str(e)}")
            
        # Return error information
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)

# ======================= Main Entry Point =======================

if __name__ == "__main__":
    log_info("Podcast TTS MCP server starting up")
    
    try:
        # Configure the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the MCP server
        log_info("Starting MCP server")
        mcp.run()
        
    except KeyboardInterrupt:
        log_info("Server stopped by user")
    except Exception as e:
        log_error(f"Server error: {e}")
