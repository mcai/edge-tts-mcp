#!/usr/bin/env python3
"""
Simple MCP wrapper script for the podcast TTS server.

This script runs the podcast_tts_mcp_server.py and ensures it uses the 
correct stdin/stdout handling required by the MCP protocol.
"""

import os
import sys
import subprocess
import logging

# Configure logging to a file
logging.basicConfig(
    filename='/tmp/podcast_tts_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filemode='w'
)

def main():
    try:
        # Log startup
        logging.info("Starting MCP wrapper")
        
        # Get path to the server script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        server_script = os.path.join(script_dir, "podcast_tts_mcp_server.py")
        
        # Log the script path
        logging.info(f"Server script path: {server_script}")
        
        # Run the server process with stdout/stderr properly configured
        proc = subprocess.Popen(
            [sys.executable, server_script],
            # Critical: use standard output for MCP protocol
            stdout=sys.stdout,
            # Everything else goes to stderr
            stderr=subprocess.PIPE,
            # Unbuffered mode is important
            bufsize=0
        )
        
        # Read stderr from the process and log it
        while True:
            line = proc.stderr.readline()
            if not line:
                break
                
            # Log the line to our log file
            logging.info(f"SERVER: {line.decode('utf-8').strip()}")
            
            # Also print to stderr for immediate feedback
            print(line.decode('utf-8').strip(), file=sys.stderr)
            
        # Wait for the process to complete
        returncode = proc.wait()
        logging.info(f"Server exited with code {returncode}")
        return returncode
        
    except Exception as e:
        logging.error(f"Wrapper error: {e}")
        print(f"Wrapper error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
