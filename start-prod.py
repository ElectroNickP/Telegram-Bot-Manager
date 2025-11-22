#!/usr/bin/env python3
"""
Telegram Bot Manager - Production Entry Point
Optimized for fast deployment on Ubuntu servers
Uses Gunicorn for production-grade serving.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major != 3 or version.minor < 11:
        print("⚠️  Warning: Python 3.11+ is recommended. Current: {}.{}.{}".format(version.major, version.minor, version.micro))
        # We don't exit, just warn
    return True

def setup_production():
    """Setup production environment"""
    print("🚀 Setting up production environment...")
    
    # Create venv if not exists
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    # Determine pip path
    if platform.system() == "Windows":
        pip_cmd = str(Path("venv") / "Scripts" / "pip")
        python_cmd = str(Path("venv") / "Scripts" / "python")
    else:
        pip_cmd = str(Path("venv") / "bin" / "pip")
        python_cmd = str(Path("venv") / "bin" / "python")

    # Install system dependencies if needed
    try:
        print("📦 Installing production dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements-prod.txt", "--quiet"], check=True)
        
        # Also install requirements.txt just in case
        if Path("requirements.txt").exists():
             subprocess.run([pip_cmd, "install", "-r", "requirements.txt", "--quiet"], check=True)
             
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def start_server():
    """Start the server using Gunicorn"""
    print(f"🌟 Starting Gunicorn server...")
    
    # Determine paths
    if platform.system() == "Windows":
        gunicorn_cmd = str((Path("venv") / "Scripts" / "gunicorn").absolute())
    else:
        gunicorn_cmd = str((Path("venv") / "bin" / "gunicorn").absolute())
        
    src_path = Path("src")
    if not src_path.exists():
        print("❌ src directory not found")
        return False
    
    # Change to src directory to make relative imports and config loading work seamlessly
    os.chdir(src_path)
    
    print(f"🌐 Web Interface: http://localhost:5000")
    print("🔐 Login: admin / securepassword123")
    
    # Start Gunicorn
    try:
        # "app:create_app()" tells gunicorn to look in app.py for create_app factory
        cmd = [gunicorn_cmd, "-c", "gunicorn_config.py", "app:create_app()"]
        print(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, env=dict(os.environ, FLASK_SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "prod-key")))
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ Gunicorn not found. Did installation fail?")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main entry point"""
    print("🚀 Telegram Bot Manager - Production Mode")
    
    if not check_python():
        sys.exit(1)
    
    if not setup_production():
        sys.exit(1)
    
    start_server()

if __name__ == "__main__":
    main()
