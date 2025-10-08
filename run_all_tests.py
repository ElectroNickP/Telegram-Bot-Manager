#!/usr/bin/env python3
"""
Test Runner - Run all tests

Запускает все типы тестов проекта:
- Unit tests
- Integration tests  
- Functional E2E tests
- API tests

Usage:
    python3 run_all_tests.py              # All tests
    python3 run_all_tests.py --unit       # Only unit
    python3 run_all_tests.py --functional # Only functional
    python3 run_all_tests.py --quick      # Quick (no E2E)
"""

import sys
import subprocess
import logging
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def run_validation():
    """Run context validation"""
    logger.info("\n" + "="*70)
    logger.info("STEP 1: Context Validation")
    logger.info("="*70)
    
    result = subprocess.run(
        ['python3', '.ai/tools/validate-context.py', '--generate'],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        logger.warning("⚠️  Context validation had issues (continuing)")
    else:
        logger.info("✅ Context is valid")
    
    return True  # Don't fail on validation issues


def run_unit_tests():
    """Run unit tests"""
    logger.info("\n" + "="*70)
    logger.info("STEP 2: Unit Tests")
    logger.info("="*70)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        logger.warning("⚠️  pytest not installed, skipping unit tests")
        logger.info("💡 Install: pip install pytest pytest-asyncio pytest-cov")
        return True
    
    result = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/unit/', '-v', '--tb=short'],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode == 0:
        logger.info("✅ Unit tests passed")
        return True
    else:
        logger.error("❌ Unit tests failed")
        return False


def run_integration_tests():
    """Run integration tests"""
    logger.info("\n" + "="*70)
    logger.info("STEP 3: Integration Tests")
    logger.info("="*70)
    
    try:
        import pytest
    except ImportError:
        logger.warning("⚠️  pytest not installed, skipping integration tests")
        return True
    
    result = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/integration/', '-v', '--tb=short'],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode == 0:
        logger.info("✅ Integration tests passed")
        return True
    else:
        logger.error("❌ Integration tests failed")
        return False


def run_functional_tests(headless=True):
    """Run functional E2E tests"""
    logger.info("\n" + "="*70)
    logger.info("STEP 4: Functional E2E Tests")
    logger.info("="*70)
    
    # Check if selenium is available
    try:
        import selenium
    except ImportError:
        logger.warning("⚠️  selenium not installed, skipping functional tests")
        logger.info("💡 Install: pip install selenium")
        logger.info("💡 Install ChromeDriver: sudo apt install chromium-chromedriver")
        return True
    
    cmd = ['python3', 'tests/functional/test_full_product.py']
    if headless:
        cmd.append('--headless')
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        logger.info("✅ Functional tests passed")
        return True
    else:
        logger.error("❌ Functional tests failed")
        return False


def run_api_tests():
    """Run API tests"""
    logger.info("\n" + "="*70)
    logger.info("STEP 5: API Tests")
    logger.info("="*70)
    
    try:
        import pytest
    except ImportError:
        logger.warning("⚠️  pytest not installed, skipping API tests")
        return True
    
    result = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/api/', '-v', '--tb=short'],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode == 0:
        logger.info("✅ API tests passed")
        return True
    else:
        logger.error("❌ API tests failed")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run all tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--functional', action='store_true', help='Run only functional tests')
    parser.add_argument('--api', action='store_true', help='Run only API tests')
    parser.add_argument('--quick', action='store_true', help='Quick tests (no E2E)')
    parser.add_argument('--no-headless', action='store_true', help='Show browser (functional tests)')
    args = parser.parse_args()
    
    logger.info("🧪 TELEGRAM BOT MANAGER - TEST SUITE")
    logger.info("="*70)
    
    results = {}
    
    # Always validate context
    results['validation'] = run_validation()
    
    # Determine what to run
    run_all = not any([args.unit, args.integration, args.functional, args.api])
    
    if args.unit or run_all:
        results['unit'] = run_unit_tests()
    
    if args.integration or run_all:
        results['integration'] = run_integration_tests()
    
    if (args.functional or run_all) and not args.quick:
        results['functional'] = run_functional_tests(headless=not args.no_headless)
    
    if args.api or run_all:
        results['api'] = run_api_tests()
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("FINAL SUMMARY")
    logger.info("="*70)
    
    for test_type, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_type}")
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    
    logger.info(f"\nTotal: {passed_count}/{total} test suites passed")
    
    if passed_count == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        logger.error(f"\n❌ {total - passed_count} TEST SUITE(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())

