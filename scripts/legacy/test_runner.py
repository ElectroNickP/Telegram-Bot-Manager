#!/usr/bin/env python3
"""
Automated Test Runner with Allure Report Generation

Runs all tests and automatically generates professional Allure reports.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRunner:
    """Automated test runner with Allure report generation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results_dir = self.project_root / "tests" / "reports" / "allure-results"
        self.report_dir = self.project_root / "tests" / "reports" / "allure-report"
        self.log_file = self.project_root / "tests" / "reports" / "test_execution.log"
        
    def setup_environment(self):
        """Setup required environment variables"""
        logger.info("Setting up environment variables...")
        
        try:
            import secrets
            jwt_key = secrets.token_hex(32)
            os.environ['JWT_SECRET_KEY'] = jwt_key
            logger.info("✅ JWT_SECRET_KEY set")
        except Exception as e:
            logger.error(f"❌ Failed to set JWT_SECRET_KEY: {e}")
            
        try:
            from cryptography.fernet import Fernet
            encryption_key = Fernet.generate_key().decode()
            os.environ['ENCRYPTION_KEY'] = encryption_key
            logger.info("✅ ENCRYPTION_KEY set")
        except Exception as e:
            logger.error(f"❌ Failed to set ENCRYPTION_KEY: {e}")
    
    def setup_directories(self):
        """Create necessary directories"""
        logger.info("Creating directories...")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directories ready")
    
    def run_tests(self):
        """Run pytest with Allure integration"""
        logger.info("")
        logger.info("╔════════════════════════════════════════════════════════════════╗")
        logger.info("║                  🧪 RUNNING TESTS WITH ALLURE                 ║")
        logger.info("╚════════════════════════════════════════════════════════════════╝")
        logger.info("")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/",
            "tests/integration/",
            "-v",
            "--tb=short",
            f"--alluredir={self.results_dir}",
            "--strict-markers",
            "--color=yes",
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        logger.info("")
        
        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode
    
    def generate_allure_report(self):
        """Generate Allure report"""
        logger.info("")
        logger.info("📊 Generating Allure Report...")
        
        if not self.results_dir.exists() or not list(self.results_dir.glob("*")):
            logger.warning("⚠️  No test results found")
            return False
        
        try:
            cmd = ["allure", "generate", str(self.results_dir), "--clean", "-o", str(self.report_dir)]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("✅ Allure Report Generated!")
            return True
        except subprocess.CalledProcessError:
            logger.warning("⚠️  Allure report generation failed (allure not installed?)")
            logger.info("Install with: npm install -g allure-commandline")
            return False
    
    def open_report(self):
        """Try to open report in browser"""
        html_file = self.report_dir / "index.html"
        
        if not html_file.exists():
            logger.warning(f"Report file not found: {html_file}")
            return
        
        try:
            import webbrowser
            webbrowser.open(f"file://{html_file}")
            logger.info(f"🌐 Opening report in browser...")
        except Exception as e:
            logger.debug(f"Could not open browser: {e}")
    
    def print_summary(self, test_exit_code):
        """Print test summary"""
        logger.info("")
        logger.info("════════════════════════════════════════════════════════════════")
        logger.info("")
        logger.info("📊 TEST SUMMARY:")
        logger.info(f"   Exit Code:    {test_exit_code}")
        logger.info(f"   Log File:     {self.log_file}")
        logger.info(f"   Report:       {self.report_dir}/index.html")
        logger.info("")
        
        if test_exit_code == 0:
            logger.info("✅ ALL TESTS PASSED!")
        else:
            logger.info(f"⚠️  TESTS FAILED (exit code: {test_exit_code})")
        
        logger.info("")
        logger.info("🌐 View Report:")
        logger.info(f"   Open: {self.report_dir}/index.html")
        logger.info(f"   Live: allure serve {self.results_dir}")
        logger.info("")
        logger.info("════════════════════════════════════════════════════════════════")
        logger.info("")
    
    def run(self):
        """Run complete test suite"""
        logger.info("")
        logger.info("╔═══════════════════════════════════════════════════════════════════════════════╗")
        logger.info("║                                                                               ║")
        logger.info("║              🧪 AUTOMATED TEST RUNNER WITH ALLURE REPORT 🧪                  ║")
        logger.info("║                                                                               ║")
        logger.info("║                      Telegram Bot Manager - Test Suite                       ║")
        logger.info("║                                                                               ║")
        logger.info("╚═══════════════════════════════════════════════════════════════════════════════╝")
        logger.info("")
        
        # Setup
        self.setup_environment()
        self.setup_directories()
        
        # Run tests
        test_exit_code = self.run_tests()
        
        # Generate report
        self.generate_allure_report()
        
        # Try to open
        self.open_report()
        
        # Summary
        self.print_summary(test_exit_code)
        
        return test_exit_code

def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

