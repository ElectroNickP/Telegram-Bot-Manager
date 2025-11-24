#!/bin/bash
# Developer Dialog Monitor - Real-time Bot Message Monitoring

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}🔍 Developer Dialog Monitor${NC}"
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
    if ! python3 -c "import aiogram" 2>/dev/null; then
        print_warning "aiogram not found, installing..."
        pip install aiogram
    fi
}

check_config() {
    if [ ! -f "bot_configs.json" ]; then
        print_error "bot_configs.json not found!"
        exit 1
    fi
    
    # Check if bot config exists
    if ! python3 -c "
import json
with open('bot_configs.json', 'r') as f:
    config = json.load(f)
    bots = config.get('bots', {})
    if not bots:
        print('No bots found')
        exit(1)
    bot_config = list(bots.values())[0]['config']
    if not bot_config.get('telegram_token'):
        print('No bot token found')
        exit(1)
" 2>/dev/null; then
        print_error "Invalid bot configuration!"
        exit 1
    fi
    
    print_success "Bot configuration valid"
}

start_monitoring() {
    print_header
    print_info "Starting real-time message monitoring..."
    
    # Check if already running
    if pgrep -f "dev_monitor.py" > /dev/null; then
        print_warning "Monitor is already running!"
        print_info "Use 'stop' to stop it first"
        return 1
    fi
    
    # Start monitoring
    print_info "🚀 Starting Developer Dialog Monitor..."
    print_info "📝 Logs will be saved to: logs/dev_monitor.log"
    print_info "🛑 Press Ctrl+C to stop monitoring"
    echo ""
    
    python3 dev_monitor.py
}

stop_monitoring() {
    print_header
    print_info "Stopping message monitoring..."
    
    if pgrep -f "dev_monitor.py" > /dev/null; then
        pkill -f "dev_monitor.py"
        print_success "Monitor stopped successfully!"
    else
        print_warning "No monitor process found"
    fi
}

show_status() {
    print_header
    print_info "Checking monitor status..."
    
    if pgrep -f "dev_monitor.py" > /dev/null; then
        PID=$(pgrep -f "dev_monitor.py")
        print_success "Monitor is running (PID: $PID)"
        
        # Show recent logs
        if [ -f "logs/dev_monitor.log" ]; then
            echo ""
            print_info "Recent activity:"
            tail -10 logs/dev_monitor.log | sed 's/^/  /'
        fi
    else
        print_warning "Monitor is not running"
    fi
}

show_logs() {
    print_header
    print_info "Showing monitor logs..."
    
    if [ -f "logs/dev_monitor.log" ]; then
        tail -f logs/dev_monitor.log
    else
        print_warning "No log file found"
    fi
}

show_help() {
    print_header
    echo "Usage: $0 {start|stop|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start real-time message monitoring"
    echo "  stop     - Stop message monitoring"
    echo "  status   - Show monitor status and recent activity"
    echo "  logs     - Show live monitor logs"
    echo "  help     - Show this help message"
    echo ""
    echo "Features:"
    echo "  • Real-time message monitoring"
    echo "  • Detailed message analysis"
    echo "  • Processing/ignoring reasons"
    echo "  • Color-coded console output"
    echo "  • Persistent log file"
    echo "  • Statistics tracking"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start monitoring"
    echo "  $0 status    # Check if running"
    echo "  $0 logs      # View live logs"
    echo "  $0 stop      # Stop monitoring"
}

# Main script logic
main() {
    # Check prerequisites
    check_python
    check_venv
    activate_venv
    check_dependencies
    check_config
    
    # Handle command
    case "${1:-help}" in
        start)
            start_monitoring
            ;;
        stop)
            stop_monitoring
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
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



