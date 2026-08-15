"""
CivicFix Root Launcher Script.
Launches the backend from either the repository root or the backend folder.

Usage:
    python run.py
    python backend/run.py
"""

import sys
import os
from pathlib import Path

# Add backend to Python path
repo_root = Path(__file__).resolve().parent
backend_dir = repo_root / "backend"

if not backend_dir.exists():
    backend_dir = repo_root

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Change working directory to backend folder so sqlite db and .env are loaded from there
os.chdir(backend_dir)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run CivicFix FastAPI Backend Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload on code change")
    args = parser.parse_args()

    print("==================================================")
    print("   CIVICFIX BACKEND SERVER STARTING")
    print(f"   API Docs:    http://{args.host}:{args.port}/docs")
    print(f"   Healthcheck: http://{args.host}:{args.port}/api/health")
    print(f"   Directory:   {backend_dir}")
    print("==================================================")

    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    except ImportError:
        print("\n[ERROR] Required dependencies are missing.")
        print("Please install requirements first by running:")
        print("    pip install -r backend/requirements.txt\n")
        sys.exit(1)
