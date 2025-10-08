#!/usr/bin/env python3
"""
Telegram Bot Manager - Professional Entry Point
Simple and reliable way to start the application with one-click setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import signal
import time
import socket
import hashlib
import getpass
import json

# PID file path  
PID_FILE = Path.cwd() / "telegram-bot-manager.pid"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print application header"""
    try:
        from __version__ import FULL_VERSION
    except ImportError:
        try:
            from src.__version__ import FULL_VERSION
        except ImportError:
            FULL_VERSION = "v3.7.6 - Complete Symlink Fix"
    
    print(f"\n{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 Telegram Bot Manager {FULL_VERSION}{Colors.END}")
    print(f"{Colors.PURPLE}{'='*60}{Colors.END}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def daemonize():
    """
    Daemonize the current process - detach from terminal and run in background
    Professional Unix daemon implementation
    """
    try:
        # First fork
        if os.fork() > 0:
            sys.exit(0)  # Exit parent process
    except OSError as e:
        print_error(f"Fork #1 failed: {e}")
        sys.exit(1)
        
    # Decouple from parent environment
    os.chdir("/")
    os.setsid() 
    os.umask(0)
    
    # Second fork  
    try:
        if os.fork() > 0:
            sys.exit(0)  # Exit second parent process
    except OSError as e:
        print_error(f"Fork #2 failed: {e}")
        sys.exit(1)
        
    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Redirect stdin/stdout/stderr to /dev/null
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'w') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

def create_pid_file():
    """Create PID file for daemon management"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        print_success(f"PID file created: {PID_FILE}")
        return True
    except Exception as e:
        print_error(f"Failed to create PID file: {e}")
        return False

def remove_pid_file():
    """Remove PID file"""
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
        return True
    except Exception as e:
        print_error(f"Failed to remove PID file: {e}")
        return False

def get_daemon_pid():
    """Get PID of running daemon"""
    try:
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
                # Check if process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    return pid
                except OSError:
                    # Process is dead, remove stale PID file
                    remove_pid_file()
                    return None
        return None
    except Exception:
        return None

def stop_daemon():
    """Stop running daemon"""
    pid = get_daemon_pid()
    if pid is None:
        print_warning("No daemon is currently running")
        return False
        
    try:
        print_info(f"Stopping daemon (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop (max 10 seconds)
        for i in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(1)
            except OSError:
                break
        else:
            # Force kill if still running
            print_warning("Daemon didn't stop gracefully, force killing...")
            os.kill(pid, signal.SIGKILL)
            
        remove_pid_file()
        print_success("Daemon stopped successfully")
        return True
        
    except OSError as e:
        print_error(f"Failed to stop daemon: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print_info(f"Received signal {signum}, shutting down...")
    remove_pid_file()
    sys.exit(0)

def find_process_by_port(port):
    """
    Find process using specific port
    Returns list of PIDs using the port
    """
    try:
        import psutil
        pids = []
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
                if connections:
                    for conn in connections:
                        if conn.laddr.port == port and conn.status == 'LISTEN':
                            pids.append(proc.info['pid'])
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return pids
    except ImportError:
        # Fallback method using netstat
        try:
            result = subprocess.run(
                ['netstat', '-tlnp'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            pids = []
            for line in result.stdout.splitlines():
                if f':{port} ' in line and 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 7 and '/' in parts[6]:
                        try:
                            pid = int(parts[6].split('/')[0])
                            pids.append(pid)
                        except (ValueError, IndexError):
                            continue
            return pids
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Final fallback using lsof
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    return [int(pid.strip()) for pid in result.stdout.split() if pid.strip().isdigit()]
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
                pass
            return []

def kill_processes_on_port(port, graceful=True):
    """
    Kill processes using specific port
    Returns True if successful, False otherwise
    """
    pids = find_process_by_port(port)
    if not pids:
        return True
        
    print_info(f"Found {len(pids)} process(es) on port {port}: {pids}")
    
    killed_pids = []
    for pid in pids:
        try:
            # Skip our own process
            if pid == os.getpid():
                continue
                
            print_info(f"Stopping process {pid} on port {port}...")
            
            if graceful:
                os.kill(pid, signal.SIGTERM)
                # Wait up to 5 seconds for graceful shutdown
                for _ in range(50):
                    try:
                        os.kill(pid, 0)  # Check if process still exists
                        time.sleep(0.1)
                    except OSError:
                        killed_pids.append(pid)
                        break
                else:
                    # If still running, force kill
                    print_warning(f"Process {pid} didn't stop gracefully, force killing...")
                    try:
                        os.kill(pid, signal.SIGKILL)
                        killed_pids.append(pid)
                    except OSError:
                        pass
            else:
                os.kill(pid, signal.SIGKILL)
                killed_pids.append(pid)
                
        except OSError as e:
            if e.errno != 3:  # Process doesn't exist
                print_warning(f"Failed to kill process {pid}: {e}")
    
    if killed_pids:
        print_success(f"Stopped {len(killed_pids)} process(es): {killed_pids}")
        # Wait a bit for ports to be released
        time.sleep(1)
        return True
    
    return False

def cleanup_port(port):
    """
    Clean up port by stopping processes using it
    Returns True if port is free, False otherwise  
    """
    # Check if port is actually in use
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:  # Port is in use
            print_info(f"Port {port} is in use, cleaning up...")
            return kill_processes_on_port(port, graceful=True)
        else:
            return True  # Port is free
            
    except Exception as e:
        print_warning(f"Error checking port {port}: {e}")
        return False

def restart_daemon(port=5000):
    """
    Restart daemon: stop existing and start new
    Professional restart with port cleanup
    """
    print_info("🔄 Restarting daemon...")
    
    # 1. Stop existing daemon if running
    existing_pid = get_daemon_pid()
    if existing_pid:
        print_info(f"Stopping existing daemon (PID: {existing_pid})...")
        stop_daemon()
    
    # 2. Clean up port
    print_info(f"Cleaning up port {port}...")
    cleanup_port(port)
    
    # 3. Wait a moment
    time.sleep(1)
    
    # 4. Verify port is free
    if not is_port_free(port):
        print_warning(f"Port {port} still in use after cleanup")
        port = find_free_port(port)
        print_info(f"Using alternative port: {port}")
    
    print_success("🔄 Ready for restart!")
    return port

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def print_question(message):
    """Print question message"""
    print(f"{Colors.CYAN}❓ {message}{Colors.END}", end='')

# ==================== NEW: Setup Helper Functions ====================

def get_password_hash(password: str) -> str:
    """Generate SHA256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()

def prompt_password(prompt: str, confirm: bool = True) -> str:
    """Prompt for password with hidden input"""
    while True:
        password = getpass.getpass(f"{Colors.CYAN}{prompt}{Colors.END}")
        if not password:
            print_error("Password cannot be empty")
            continue
        if len(password) < 4:
            print_error("Password must be at least 4 characters")
            continue
        if confirm:
            password2 = getpass.getpass(f"{Colors.CYAN}Confirm password: {Colors.END}")
            if password != password2:
                print_error("Passwords don't match")
                continue
        return password

def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt for input with default value"""
    print_question(f"{prompt} [{default}]: ")
    value = input().strip()
    return value if value else default

def first_time_setup() -> bool:
    """
    Interactive first-time setup wizard
    Creates .env file with admin credentials and configuration
    """
    print(f"\n{Colors.PURPLE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}🔧 First-Time Setup Wizard{Colors.END}")
    print(f"{Colors.PURPLE}{'='*70}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}This wizard will help you set up your Telegram Bot Manager.{Colors.END}\n")
    
    try:
        # 1. Admin credentials
        print(f"{Colors.BOLD}1. Admin Credentials{Colors.END}")
        username = prompt_with_default("Admin username", "admin")
        password = prompt_password("Admin password: ")
        password_hash = get_password_hash(password)
        print_success("Credentials configured\n")
        
        # 2. Server configuration
        print(f"{Colors.BOLD}2. Server Configuration{Colors.END}")
        port = prompt_with_default("Default port", "5000")
        host = prompt_with_default("Default host (0.0.0.0 for all interfaces)", "0.0.0.0")
        print_success("Server configured\n")
        
        # 3. Create .env file
        print(f"{Colors.BOLD}3. Creating Configuration{Colors.END}")
        env_content = f"""# Telegram Bot Manager Configuration
# Generated by setup wizard on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Admin credentials
ADMIN_USERNAME={username}
ADMIN_PASSWORD_HASH={password_hash}

# Server configuration
DEFAULT_PORT={port}
DEFAULT_HOST={host}

# Security
SECRET_KEY={hashlib.sha256(os.urandom(32)).hexdigest()}
"""
        
        env_path = Path.cwd() / ".env"
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print_success(f"Configuration saved to {env_path}")
        
        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Setup Complete!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Your admin credentials:{Colors.END}")
        print(f"  Username: {Colors.BOLD}{username}{Colors.END}")
        print(f"  Password: {Colors.BOLD}{'*' * len(password)}{Colors.END}")
        print(f"\n{Colors.YELLOW}⚠️  Please save these credentials in a secure place!{Colors.END}\n")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        return False
    except Exception as e:
        print_error(f"Setup failed: {e}")
        return False

def validate_env() -> bool:
    """
    Validate .env file exists and contains required variables
    """
    env_path = Path.cwd() / ".env"
    
    if not env_path.exists():
        print_warning(".env file not found")
        print_info("Starting first-time setup wizard...\n")
        return first_time_setup()
    
    # Load .env and check required vars
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        required_vars = ['ADMIN_USERNAME', 'ADMIN_PASSWORD_HASH']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print_error(f"Missing required variables in .env: {', '.join(missing_vars)}")
            print_info("Re-running setup wizard...\n")
            # Backup old .env
            backup_path = env_path.with_suffix('.env.backup')
            env_path.rename(backup_path)
            print_info(f"Old .env backed up to {backup_path}")
            return first_time_setup()
        
        return True
        
    except Exception as e:
        print_error(f"Failed to validate .env: {e}")
        return False

def check_config_files() -> bool:
    """
    Check and create required configuration files and directories
    """
    try:
        # 1. Create logs directory
        logs_dir = Path.cwd() / "logs"
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True)
            print_success("Created logs/ directory")
        
        # 2. Create backups directory
        backups_dir = Path.cwd() / "backups"
        if not backups_dir.exists():
            backups_dir.mkdir(parents=True)
            print_success("Created backups/ directory")
        
        # 3. Create bot_configs.json if missing
        config_path = Path.cwd() / "bot_configs.json"
        if not config_path.exists():
            default_config = {
                "bots": {},
                "conversations": {},
                "user_sessions": {},
                "online_users": {}
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print_success("Created bot_configs.json")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create config files: {e}")
        return False

def print_success_banner(port: int, host: str):
    """Print success banner with access information"""
    print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ Telegram Bot Manager STARTED{Colors.END}")
    print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
    
    # Load admin username from .env
    username = "admin"  # default
    try:
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ADMIN_USERNAME='):
                        username = line.split('=', 1)[1].strip()
                        break
    except:
        pass
    
    # Determine URLs
    if host == "0.0.0.0":
        urls = [
            f"http://localhost:{port}",
            f"http://127.0.0.1:{port}"
        ]
        # Try to get local IP
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip and local_ip != "127.0.0.1":
                urls.append(f"http://{local_ip}:{port}")
        except:
            pass
    else:
        urls = [f"http://{host}:{port}"]
    
    print(f"{Colors.BOLD}🌐 Web Interface:{Colors.END}")
    for url in urls:
        print(f"   {url}")
    print()
    
    print(f"{Colors.BOLD}🔐 Admin Login:{Colors.END} {username}")
    print(f"{Colors.BOLD}📊 API Docs:{Colors.END} {urls[0]}/api/v2/docs")
    print(f"{Colors.BOLD}📝 Logs:{Colors.END} tail -f logs/app.log\n")
    
    print(f"{Colors.YELLOW}🛑 To stop:{Colors.END}")
    print(f"   Interactive mode: {Colors.BOLD}Ctrl+C{Colors.END}")
    print(f"   Daemon mode:      {Colors.BOLD}python3 start.py --stop{Colors.END}\n")
    
    print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")

# ==================== Existing Functions ====================

def check_python_version():
    """Check if Python version is compatible"""
    print_info("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True

def check_virtual_env():
    """Check and activate virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_warning("Virtual environment not found. Creating...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print_success("Virtual environment created")
        except subprocess.CalledProcessError:
            print_error("Failed to create virtual environment")
            return False
    
    # ALWAYS use venv Python, regardless of current environment
    # The old logic was buggy and returned system Python
    
    # Get activation script path
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
    
    if not activate_script.exists():
        print_error("Virtual environment activation script not found")
        return False
    
    print_success("Virtual environment ready")
    # Return absolute path but DON'T resolve symlinks (venv/bin/python → /usr/bin/python3.12)
    return python_exe.absolute()

def install_dependencies(python_exe):
    """Install required dependencies"""
    print_info("Checking dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print_error("requirements.txt not found")
            return False
        
        # Install dependencies
        subprocess.run([
            str(python_exe), "-m", "pip", "install", "-r", "requirements.txt", "--quiet"
        ], check=True)
        
        # Install in editable mode only if pyproject.toml exists
        if Path("pyproject.toml").exists():
            subprocess.run([
                str(python_exe), "-m", "pip", "install", "-e", ".", "--quiet"
            ], check=True)
        else:
            print_warning("pyproject.toml not found, skipping editable install")
        
        print_success("Dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def is_port_free(port):
    """Check if a port is free"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

def find_free_port(start_port=5000):
    """Find a free port starting from start_port"""
    
    for port in range(start_port, start_port + 100):
        if is_port_free(port):
            return port
    return start_port

def start_application(python_exe, port=5000, host='127.0.0.1', daemon=False):
    """Start the Flask application"""
    print_info(f"Starting application on {host}:{port}...")
    
    # Get absolute path to python executable before changing directory (don't resolve symlinks!)
    python_exe_abs = Path(python_exe).absolute()
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    env['FLASK_APP'] = 'src.app'
    env['FLASK_ENV'] = 'development'
    
    try:
        # Change to src directory and run app
        os.chdir("src")
        
        if not daemon:
            print_success("🌟 Application starting...")
            print_info(f"🌐 Web Interface: http://{host}:{port}")
            print_info("🔐 Login credentials:")
            print(f"   📧 Username: {Colors.BOLD}admin{Colors.END}")
            print(f"   🔑 Password: {Colors.BOLD}securepassword123{Colors.END}")
            print_info(f"🏪 ElectroNick bot Market: http://{host}:{port}/marketplace")
            print_warning("Press Ctrl+C to stop the server\n")
        
        # Run the application
        subprocess.run([
            str(python_exe_abs), "app.py"
        ], env=env, check=True)
        
    except KeyboardInterrupt:
        print_info("\n👋 Application stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start application: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir("..")

def main():
    """Main entry point"""
    print_header()
    
    try:
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # NEW: Step 1 - Validate/Create .env configuration
        if not validate_env():
            print_error("Configuration setup failed")
            sys.exit(1)
        
        # NEW: Step 2 - Check/Create required files and directories
        if not check_config_files():
            print_error("Failed to create required files")
            sys.exit(1)
        
        # Step 3: Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Step 4: Setup virtual environment
        python_exe = check_virtual_env()
        if not python_exe:
            sys.exit(1)
        
        # Step 5: Install dependencies
        if not install_dependencies(python_exe):
            sys.exit(1)
        
        # Step 6: Find free port
        port = find_free_port()
        if port != 5000:
            print_warning(f"Port 5000 is busy, using port {port}")
        
        # Check for daemon mode
        daemon_mode = '--daemon' in sys.argv or '-d' in sys.argv
        
        if daemon_mode:
            # Check if daemon is already running and clean up port
            existing_pid = get_daemon_pid()
            if existing_pid:
                print_info(f"Found existing daemon (PID: {existing_pid}), stopping it...")
                stop_daemon()
            
            # Clean up port 5000 from any previous processes
            print_info("🧹 Cleaning up port 5000 from previous instances...")
            if cleanup_port(5000):
                print_success("✅ Port 5000 is now free")
                port = 5000  # Use default port since it's free
            else:
                print_warning("⚠️ Could not free port 5000, will find alternative port")
                port = find_free_port()
            
            print_info("Starting in daemon mode...")
            print_success("🌟 Daemon will start in background")
            
            # Show banner before daemonizing
            print_success_banner(port, "0.0.0.0")
            
            print_info(f"📄 PID file: {PID_FILE}")
            print_info("Use 'python start.py --stop' to stop the daemon")
            print_info("Use 'python start.py --status' to check daemon status")
            
            # Return to original directory before daemonizing
            original_dir = Path.cwd()
            
            # Daemonize the process
            daemonize()
            
            # After daemonization, we're in a new process
            # Change back to original directory
            os.chdir(str(original_dir))
            
            # Setup signal handlers  
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Create PID file
            create_pid_file()
        
        # Step 5: Start application
        if not daemon_mode:
            # Show banner for interactive mode
            print_success_banner(port, "127.0.0.1")
        
        success = start_application(python_exe, port, daemon=daemon_mode)
        
        if success:
            print_success("Application stopped successfully")
        else:
            print_error("Application encountered errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_info("\n👋 Setup interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

def print_help():
    """Print help information"""
    try:
        from __version__ import FULL_VERSION
    except ImportError:
        try:
            from src.__version__ import FULL_VERSION
        except ImportError:
            FULL_VERSION = "v3.7.6 - Complete Symlink Fix"
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Telegram Bot Manager - Professional Entry Point{Colors.END}")
    print(f"{Colors.GREEN}Simple and reliable way to start the application{Colors.END}\n")
    
    print(f"{Colors.BOLD}Usage:{Colors.END}")
    print("  python start.py              - Start in interactive mode")
    print("  python start.py --daemon     - Start as background daemon")  
    print("  python start.py -d           - Start as background daemon (short)")
    print("  python start.py --stop       - Stop running daemon")
    print("  python start.py --restart    - Restart daemon (stop + clean port + start)")
    print("  python start.py --status     - Check daemon status")
    print("  python start.py --help       - Show this help message")
    print("  python start.py -h           - Show this help message")
    
    print(f"\n{Colors.BOLD}Background Service (Recommended for Production):{Colors.END}")
    print("  ./service-install.sh         - Install as systemd service")
    print("  ./service-manager.sh start   - Start service in background")
    print("  ./service-manager.sh stop    - Stop background service") 
    print("  ./service-manager.sh status  - Check service status")
    print("  ./service-manager.sh logs    - View live logs")
    print("  ./service-manager.sh --help  - Service manager help")
    
    print(f"\n{Colors.BOLD}Features:{Colors.END}")
    print("  • Automatic virtual environment setup")
    print("  • Dependency installation and verification")
    print("  • Port detection and conflict resolution")
    print("  • True Unix daemon mode (detaches from terminal)")
    print("  • PID file management for daemon control")
    print("  • Graceful shutdown with signal handling")
    print("  • Automatic port cleanup and process management")
    print("  • Smart restart with previous instance cleanup")
    print("  • Systemd service integration")
    print("  • Professional error handling")
    print("  • Production-ready deployment")
    
    print(f"\nVersion: {FULL_VERSION}")
    print(f"Documentation: {Colors.CYAN}BACKGROUND_SERVICE_GUIDE.md{Colors.END}\n")

if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)
    
    # Check for stop flag
    if '--stop' in sys.argv:
        stop_daemon()
        sys.exit(0)
        
    # Check for restart flag
    if '--restart' in sys.argv:
        port = restart_daemon()
        # Continue with normal startup but use cleaned port
        sys.argv.append('--daemon')  # Force daemon mode on restart
        
    # Check for status flag
    if '--status' in sys.argv:
        pid = get_daemon_pid()
        if pid:
            print_success(f"Daemon is running (PID: {pid})")
            print_info(f"PID file: {PID_FILE}")
            try:
                # Try to get process info
                import psutil
                process = psutil.Process(pid)
                print_info(f"CPU: {process.cpu_percent()}%")
                print_info(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
                print_info(f"Started: {process.create_time()}")
            except ImportError:
                print_info("Install psutil for detailed process info: pip install psutil")
            except Exception:
                pass
        else:
            print_warning("No daemon is currently running")
        sys.exit(0)
    
    main()
