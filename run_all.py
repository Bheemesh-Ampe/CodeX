"""
CivicFix Full-Stack Application Launcher (Backend + Frontend).

Launches:
- Backend Server:   http://127.0.0.1:8000 (API Docs: http://127.0.0.1:8000/docs)
- Frontend Web App: http://127.0.0.1:3000

Usage:
    python run_all.py
    (or double-click start_all.bat)
"""

import sys
import os
import time
import threading
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

# Determine paths
repo_root = Path(__file__).resolve().parent
backend_dir = repo_root / "backend"
frontend_dir = repo_root / "frontend"


class FrontendHandler(SimpleHTTPRequestHandler):
    """Serve files from the frontend directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(frontend_dir), **kwargs)

    def log_message(self, format, *args):
        # Silence routine static asset HTTP logs for clean terminal output
        pass


def run_backend():
    """Start the FastAPI backend server on port 8000."""
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")


def run_frontend():
    """Start the HTTP server serving the frontend on port 3000."""
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", 3000), FrontendHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    print("==================================================================")
    print("                CIVICFIX FULL-STACK APPLICATION                   ")
    print("==================================================================")
    print("   🌐 Resident & Admin Web Portal: http://127.0.0.1:3000")
    print("   ⚙️ FastAPI Interactive API Docs: http://127.0.0.1:8000/docs")
    print("   🏥 Backend Healthcheck:         http://127.0.0.1:8000/api/health")
    print("==================================================================")
    print("🚀 Starting Backend & Frontend servers...")
    print("⌨️  Press CTRL+C in this terminal window to stop both servers.\n")

    # 1. Launch backend in background daemon thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give backend a moment to bind port 8000
    time.sleep(1.5)

    # 2. Automatically launch default browser to Frontend
    try:
        webbrowser.open("http://127.0.0.1:3000")
    except Exception:
        pass

    # 3. Run frontend HTTP server on main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Stopping CivicFix Full-Stack application. Goodbye!")
        sys.exit(0)
