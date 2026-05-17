#!/usr/bin/env python3
"""
Field Mind - Quick Start Script
Runs the FastAPI application with proper configuration
"""

import os
import sys
from pathlib import Path


def main():
    """Run the FastAPI application."""
    # Change to backend directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        sys.exit(1)
    
    # Check if .env exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your credentials.")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("="*60)
    print("🚀 Starting Field Mind Application")
    print("="*60)
    print()
    print("📍 Backend directory:", backend_dir)
    print("🌐 Server will start at: http://localhost:8000")
    print("📱 Frontend available at: http://localhost:8000/static/index.html")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    # Run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed!")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Field Mind...")
        sys.exit(0)


if __name__ == "__main__":
    main()

# Made with Bob
