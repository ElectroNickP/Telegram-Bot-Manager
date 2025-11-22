#!/usr/bin/env python3
"""
Process Manager for Telegram Bot Manager
Prevents multiple instances and provides proper process management
"""

import os
import sys
import signal
import psutil
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ProcessManager:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.pid_file = self.project_root / "telegram_bot_manager.pid"
        self.config_file = self.project_root / "process_config.json"
        self.port = 5000  # Fixed port
        self.process_name = "telegram_bot_manager"
        
    def is_running(self) -> bool:
        """Check if the process is already running"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and is our process
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                if self.process_name in ' '.join(process.cmdline()):
                    return True
                    
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        # Clean up stale PID file
        self.pid_file.unlink(missing_ok=True)
        return False
    
    def get_running_process_info(self) -> Optional[Dict[str, Any]]:
        """Get information about running process"""
        if not self.pid_file.exists():
            return None
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                return {
                    'pid': pid,
                    'start_time': process.create_time(),
                    'memory': process.memory_info().rss,
                    'cpu_percent': process.cpu_percent(),
                    'status': process.status(),
                    'cmdline': ' '.join(process.cmdline())
                }
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return None
    
    def is_port_in_use(self) -> bool:
        """Check if our port is already in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == self.port and conn.status == 'LISTEN':
                return True
        return False
    
    def kill_existing_process(self) -> bool:
        """Kill existing process if running"""
        if not self.is_running():
            return True
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown failed
                process.kill()
                process.wait(timeout=5)
            
            self.pid_file.unlink(missing_ok=True)
            return True
            
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error killing process: {e}")
            return False
    
    def save_pid(self, pid: int):
        """Save process PID to file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
    
    def save_config(self, config: Dict[str, Any]):
        """Save process configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        """Load process configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Cleanup PID file and other resources"""
        self.pid_file.unlink(missing_ok=True)
        print("✅ Cleanup completed")
    
    def start(self, force: bool = False) -> bool:
        """Start the process with proper checks"""
        print("🔍 Checking for existing processes...")
        
        if self.is_running():
            if not force:
                info = self.get_running_process_info()
                if info:
                    print(f"❌ Process already running!")
                    print(f"   PID: {info['pid']}")
                    print(f"   Started: {time.ctime(info['start_time'])}")
                    print(f"   Memory: {info['memory'] / 1024 / 1024:.1f} MB")
                    print(f"   Status: {info['status']}")
                    print(f"   Command: {info['cmdline']}")
                    print(f"\n💡 Use --force to kill existing process and start new one")
                    return False
                else:
                    print("⚠️ Stale PID file found, cleaning up...")
                    self.pid_file.unlink(missing_ok=True)
            else:
                print("🛑 Force mode: killing existing process...")
                if not self.kill_existing_process():
                    print("❌ Failed to kill existing process")
                    return False
                time.sleep(2)  # Wait for cleanup
        
        if self.is_port_in_use():
            print(f"❌ Port {self.port} is already in use!")
            print("💡 Another process is using the port")
            return False
        
        print("✅ No conflicts found, starting process...")
        
        # Save current PID
        self.save_pid(os.getpid())
        
        # Save configuration
        config = {
            'start_time': time.time(),
            'port': self.port,
            'project_root': str(self.project_root),
            'python_version': sys.version,
            'process_name': self.process_name
        }
        self.save_config(config)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        print(f"✅ Process started successfully!")
        print(f"   PID: {os.getpid()}")
        print(f"   Port: {self.port}")
        print(f"   PID file: {self.pid_file}")
        print(f"   Config file: {self.config_file}")
        
        return True
    
    def status(self) -> Dict[str, Any]:
        """Get current status"""
        status = {
            'running': self.is_running(),
            'port_in_use': self.is_port_in_use(),
            'pid_file_exists': self.pid_file.exists(),
            'config_file_exists': self.config_file.exists(),
            'port': self.port
        }
        
        if status['running']:
            info = self.get_running_process_info()
            if info:
                status.update(info)
        
        return status

def main():
    """CLI interface for process manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Bot Manager Process Manager')
    parser.add_argument('action', choices=['start', 'stop', 'status', 'kill'], 
                       help='Action to perform')
    parser.add_argument('--force', action='store_true', 
                       help='Force action (kill existing process)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to use (default: 5000)')
    
    args = parser.parse_args()
    
    manager = ProcessManager()
    manager.port = args.port
    
    if args.action == 'start':
        if manager.start(force=args.force):
            print("🚀 Process manager ready!")
            return True
        else:
            return False
    
    elif args.action == 'stop':
        if manager.is_running():
            if manager.kill_existing_process():
                print("✅ Process stopped successfully")
            else:
                print("❌ Failed to stop process")
                return False
        else:
            print("ℹ️ No process running")
        return True
    
    elif args.action == 'status':
        status = manager.status()
        print("📊 Process Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        return True
    
    elif args.action == 'kill':
        if manager.kill_existing_process():
            print("✅ Process killed successfully")
        else:
            print("❌ Failed to kill process")
            return False
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)



