#!/usr/bin/env python3
"""
STYLUX AI Fashion Assistant - Quick Start Script
This script helps you start both the frontend and backend servers.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python():
    """Check if Python is available."""
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_node():
    """Check if Node.js is available."""
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_npm():
    """Check if npm is available."""
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def find_npm():
    """Try to find npm in common locations."""
    possible_paths = [
        "npm",
        "npm.cmd",
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd"),
    ]
    
    for path in possible_paths:
        try:
            subprocess.run([path, "--version"], check=True, capture_output=True)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    if not check_python():
        print("❌ Python is not installed or not in PATH")
        print("   Please install Python from: https://python.org")
        return False
    
    if not check_node():
        print("❌ Node.js is not installed or not in PATH")
        print("   Please install Node.js from: https://nodejs.org")
        return False
    
    npm_path = find_npm()
    if not npm_path:
        print("❌ npm is not found")
        print("   Please ensure Node.js is properly installed")
        return False
    
    print("✅ Dependencies check passed")
    return True

def setup_backend():
    """Setup and start the backend server."""
    print("\n🚀 Setting up backend...")
    
    backend_dir = Path("Stylux/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        import pandas
        import google.generativeai
    except ImportError:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "Stylux/backend/requirments.txt"], check=True)
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("📝 Creating backend .env file...")
        with open(env_file, "w") as f:
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")
        print("⚠️  Please update the GOOGLE_API_KEY in Stylux/backend/.env")
    
    return True

def setup_frontend():
    """Setup the frontend."""
    print("\n🎨 Setting up frontend...")
    
    frontend_dir = Path("front-end")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing Node.js dependencies...")
        npm_path = find_npm()
        if npm_path:
            subprocess.run([npm_path, "install"], cwd=frontend_dir, check=True)
        else:
            print("❌ npm not found. Please install Node.js properly.")
            return False
    
    # Check if .env.local exists
    env_file = frontend_dir / ".env.local"
    if not env_file.exists():
        print("📝 Creating frontend .env.local file...")
        with open(env_file, "w") as f:
            f.write("VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key_here\n")
            f.write("VITE_API_BASE_URL=http://localhost:8000\n")
        print("⚠️  Please update the VITE_CLERK_PUBLISHABLE_KEY in front-end/.env.local")
    
    return True

def start_servers():
    """Start both frontend and backend servers."""
    print("\n🌟 Starting STYLUX AI servers...")
    
    # Start backend
    print("🔧 Starting backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "Stylux/backend/start_server.py"
    ])
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🎨 Starting frontend server...")
    npm_path = find_npm()
    if not npm_path:
        print("❌ npm not found. Please install Node.js properly.")
        print("   Download from: https://nodejs.org")
        backend_process.terminate()
        return
    
    try:
        frontend_process = subprocess.Popen([
            npm_path, "run", "dev"
        ], cwd="front-end")
        
        print("\n🎉 STYLUX AI is starting up!")
        print("📍 Frontend: http://localhost:5173")
        print("🔧 Backend: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n⏳ Opening frontend in browser...")
        
        # Open browser after a short delay
        time.sleep(5)
        webbrowser.open("http://localhost:5173")
        
        try:
            print("\n🔄 Servers are running. Press Ctrl+C to stop...")
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Servers stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        print("💡 Try running manually:")
        print("   cd front-end")
        print("   npm run dev")
        backend_process.terminate()

def main():
    """Main function."""
    print("=" * 60)
    print("🎨 STYLUX AI Fashion Assistant - Quick Start")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install the required dependencies:")
        print("   - Python 3.8+: https://python.org")
        print("   - Node.js 16+: https://nodejs.org")
        print("\n💡 After installing Node.js, restart your terminal/command prompt")
        return
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return
    
    # Start servers
    start_servers()

if __name__ == "__main__":
    main() 