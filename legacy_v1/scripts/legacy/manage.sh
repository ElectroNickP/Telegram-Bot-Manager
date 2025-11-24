#!/bin/bash
# Telegram Bot Manager - Process Management Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}🚀 Telegram Bot Manager - Process Management${NC}"
    echo "=================================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found!"
        exit 1
    fi
}

check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found!"
        print_info "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
}

activate_venv() {
    source venv/bin/activate
    print_success "Virtual environment activated"
}

check_dependencies() {
    if ! python3 -c "import psutil" 2>/dev/null; then
        print_warning "psutil not found, installing..."
        pip install psutil
    fi
}

show_status() {
    print_header
    print_info "Checking process status..."
    
    if python3 process_manager.py status; then
        print_success "Status check completed"
    else
        print_error "Status check failed"
        exit 1
    fi
}

start_process() {
    print_header
    print_info "Starting Telegram Bot Manager..."
    
    # Check if already running
    if python3 process_manager.py status | grep -q "running.*True"; then
        print_warning "Process is already running!"
        print_info "Use 'stop' to stop it first, or 'restart' to restart"
        return 1
    fi
    
    # Start the process
    if python3 start_smart.py; then
        print_success "Telegram Bot Manager started successfully!"
    else
        print_error "Failed to start Telegram Bot Manager"
        exit 1
    fi
}

stop_process() {
    print_header
    print_info "Stopping Telegram Bot Manager..."
    
    if python3 process_manager.py stop; then
        print_success "Telegram Bot Manager stopped successfully!"
    else
        print_error "Failed to stop Telegram Bot Manager"
        exit 1
    fi
}

restart_process() {
    print_header
    print_info "Restarting Telegram Bot Manager..."
    
    # Stop first
    if python3 process_manager.py status | grep -q "running.*True"; then
        print_info "Stopping existing process..."
        python3 process_manager.py stop
        sleep 2
    fi
    
    # Start new
    print_info "Starting new process..."
    if python3 start_smart.py; then
        print_success "Telegram Bot Manager restarted successfully!"
    else
        print_error "Failed to restart Telegram Bot Manager"
        exit 1
    fi
}

kill_process() {
    print_header
    print_warning "Force killing Telegram Bot Manager..."
    
    if python3 process_manager.py kill; then
        print_success "Process killed successfully!"
    else
        print_error "Failed to kill process"
        exit 1
    fi
}

show_help() {
    print_header
    echo "Usage: $0 {start|stop|restart|status|kill|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start Telegram Bot Manager (with conflict detection)"
    echo "  stop     - Stop Telegram Bot Manager gracefully"
    echo "  restart  - Restart Telegram Bot Manager"
    echo "  status   - Show current process status"
    echo "  kill     - Force kill process (use with caution)"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the manager"
    echo "  $0 status    # Check if running"
    echo "  $0 restart   # Restart if needed"
    echo "  $0 stop      # Stop gracefully"
}

# Main script logic
main() {
    # Check prerequisites
    check_python
    check_venv
    activate_venv
    check_dependencies
    
    # Handle command
    case "${1:-help}" in
        start)
            start_process
            ;;
        stop)
            stop_process
            ;;
        restart)
            restart_process
            ;;
        status)
            show_status
            ;;
        kill)
            kill_process
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"



