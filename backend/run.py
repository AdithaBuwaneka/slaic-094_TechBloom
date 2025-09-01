#!/usr/bin/env python3
"""
Smart Transit Companion Backend Runner
SLAIC 2025 - Easy server startup script
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Run the FastAPI server with optimal settings"""
    
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("ERROR: .env file not found!")
        print("Please copy .env.example to .env and configure your settings")
        sys.exit(1)
    
    # Check if all required directories exist
    required_dirs = ["app", "logs", "scripts"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"ERROR: Required directory '{dir_name}' not found!")
            sys.exit(1)
    
    print("Starting Smart Transit Companion Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Press CTRL+C to stop the server")
    print("-" * 60)
    
    try:
        # Run the server with optimal production settings
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,           # Auto-reload for development
            reload_dirs=["app"],   # Only watch app directory
            log_level="info",
            access_log=True,
            use_colors=True,
            loop="auto",
            workers=1              # Single worker for development
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        print("Thank you for using Smart Transit Companion!")
    except Exception as e:
        print(f"ERROR: Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()