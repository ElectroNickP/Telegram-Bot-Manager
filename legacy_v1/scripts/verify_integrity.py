
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path.cwd()
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

print(f"Checking imports from {project_root}")

try:
    print("1. Testing Config Manager...")
    import src.config_manager as cm
    print("   ✅ Config Manager imported")
    
    print("2. Testing Bot Manager...")
    import src.bot_manager as bm
    print("   ✅ Bot Manager imported")
    
    print("3. Testing Flask App Factory...")
    from src.app import create_app
    print("   ✅ App Factory imported")
    
    print("4. Testing Web Routes...")
    import src.web.routes
    print("   ✅ Web Routes imported")
    
    print("5. Testing Gunicorn Config...")
    import src.gunicorn_config
    print("   ✅ Gunicorn Config imported")

    print("\n✅ SYSTEM INTEGRITY CHECK PASSED")
    sys.exit(0)
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    sys.exit(1)

