#!/usr/bin/env python3
"""
Test script for first-time setup wizard
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import setup functions from start.py
from start import (
    validate_env,
    check_config_files,
    get_password_hash,
    Colors,
    print_success,
    print_error,
    print_info
)

def test_setup():
    """Test setup functions without running full start.py"""
    print(f"\n{Colors.CYAN}Testing Phase 2: One-Click Install{Colors.END}\n")
    
    # Test 1: check_config_files
    print(f"{Colors.BOLD}Test 1: check_config_files(){Colors.END}")
    if check_config_files():
        print_success("Config files check passed")
        
        # Verify files exist
        if Path("logs").exists():
            print_success("  - logs/ directory exists")
        if Path("backups").exists():
            print_success("  - backups/ directory exists")
        if Path("bot_configs.json").exists():
            print_success("  - bot_configs.json exists")
            import json
            with open("bot_configs.json") as f:
                config = json.load(f)
                if all(k in config for k in ["bots", "conversations", "user_sessions", "online_users"]):
                    print_success("  - bot_configs.json structure valid")
    else:
        print_error("Config files check failed")
        return False
    
    print()
    
    # Test 2: get_password_hash
    print(f"{Colors.BOLD}Test 2: get_password_hash(){Colors.END}")
    test_password = "admin"
    expected_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    actual_hash = get_password_hash(test_password)
    if actual_hash == expected_hash:
        print_success(f"Password hash correct: {actual_hash[:16]}...")
    else:
        print_error(f"Password hash mismatch!")
        return False
    
    print()
    
    # Test 3: .env validation (with existing file)
    print(f"{Colors.BOLD}Test 3: validate_env() with existing .env{Colors.END}")
    if Path(".env").exists():
        if validate_env():
            print_success(".env validation passed")
            # Check contents
            with open(".env") as f:
                content = f.read()
                if "ADMIN_USERNAME=" in content:
                    print_success("  - ADMIN_USERNAME present")
                if "ADMIN_PASSWORD_HASH=" in content:
                    print_success("  - ADMIN_PASSWORD_HASH present")
        else:
            print_error(".env validation failed")
            return False
    else:
        print_info(".env doesn't exist (this would trigger wizard)")
    
    print()
    
    print(f"{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ All tests passed!{Colors.END}")
    print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


