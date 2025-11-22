#!/usr/bin/env python3
"""
Smart startup script for Telegram Bot Manager
Prevents multiple instances and provides proper process management
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import psutil
        return True
    except ImportError:
        print("❌ psutil not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
        return True

def main():
    """Main startup function"""
    print("🚀 Telegram Bot Manager - Smart Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Import process manager
    from process_manager import ProcessManager
    
    # Initialize process manager
    manager = ProcessManager()
    
    # Check if already running
    if manager.is_running():
        print("❌ Telegram Bot Manager is already running!")
        info = manager.get_running_process_info()
        if info:
            print(f"   PID: {info['pid']}")
            print(f"   Started: {time.ctime(info['start_time'])}")
            print(f"   Memory: {info['memory'] / 1024 / 1024:.1f} MB")
            print(f"   Status: {info['status']}")
        print("\n💡 Use 'python3 start_smart.py --force' to restart")
        print("💡 Use 'python3 process_manager.py stop' to stop")
        return False
    
    # Check port availability
    if manager.is_port_in_use():
        print(f"❌ Port {manager.port} is already in use!")
        print("💡 Another process is using the port")
        return False
    
    # Start process manager
    if not manager.start():
        print("❌ Failed to start process manager")
        return False
    
    print("\n🎯 Starting Telegram Bot Manager...")
    print(f"   Port: {manager.port}")
    print(f"   PID: {os.getpid()}")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the actual application
        from start import main as start_main
        start_main()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        manager.cleanup()
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        manager.cleanup()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)



