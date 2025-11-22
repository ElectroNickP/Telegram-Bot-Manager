# 🧪 Test Execution & Allure Report Guide

**Date**: October 18, 2025  
**Status**: COMPLETE - Automated Test Runner Ready  

---

## 📋 Overview

This guide explains how to run tests with automatic Allure report generation for the Telegram Bot Manager project.

---

## 🚀 Quick Start

### Option 1: Python Runner (Recommended)
```bash
python3 test_runner.py
```

### Option 2: Bash Script
```bash
./run_tests_with_report.sh
```

### Option 3: Direct Pytest
```bash
pytest tests/unit/ tests/integration/ -v --alluredir=tests/reports/allure-results
allure serve tests/reports/allure-results
```

---

## 📊 What Gets Tested

### Test Categories

```
✅ Unit Tests (91 tests)
├─ Authentication (17 tests)
│  ├─ Password hashing
│  ├─ Password validation
│  ├─ Password change
│  └─ Password verification
├─ Crypto Service (34 tests)
│  ├─ Encryption/Decryption
│  ├─ Field detection
│  ├─ Dictionary operations
│  └─ Edge cases
├─ JWT Service (26 tests)
│  ├─ Token creation
│  ├─ Token verification
│  ├─ API tokens
│  └─ Token extraction
├─ Security Headers (8 tests)
│  ├─ HTTPS redirect
│  ├─ HSTS headers
│  ├─ XSS protection
│  └─ CORS headers
└─ Storage Interface (11 tests)
   ├─ Conversation CRUD
   ├─ Cleanup operations
   └─ Cache management

✅ Integration Tests (32 tests)
├─ Adapters
├─ Auth Flow
└─ API Endpoints
```

---

## 🎯 Test Commands

### Run All Tests
```bash
python3 test_runner.py
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -v --alluredir=tests/reports/allure-results
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -v --alluredir=tests/reports/allure-results
```

### Run Specific Test File
```bash
pytest tests/unit/test_jwt_service.py -v --alluredir=tests/reports/allure-results
```

### Run Tests with Marker
```bash
pytest -m security -v --alluredir=tests/reports/allure-results
pytest -m critical -v --alluredir=tests/reports/allure-results
pytest -m "not slow" -v --alluredir=tests/reports/allure-results
```

---

## 📊 Allure Report

### Auto-Generated Report
After running tests, report is automatically generated at:
```
tests/reports/allure-report/index.html
```

### View Report

#### Static HTML
```bash
open tests/reports/allure-report/index.html
# or
firefox tests/reports/allure-report/index.html
```

#### Live Server
```bash
allure serve tests/reports/allure-results
```

This will start a web server at `http://localhost:4040` with live report.

---

## 🔧 Environment Setup

### Required Environment Variables
The test runner automatically sets:

```bash
JWT_SECRET_KEY=<random 64-char hex>
ENCRYPTION_KEY=<Fernet encryption key>
```

### Manual Setup (if needed)
```bash
# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Export to environment
export JWT_SECRET_KEY=<value>
export ENCRYPTION_KEY=<value>
```

---

## 📈 Test Markers

### Available Markers
```bash
# View all markers
pytest --markers

# Run only critical tests
pytest -m critical -v

# Run only security tests
pytest -m security -v

# Run tests except slow ones
pytest -m "not slow" -v

# Run unit tests
pytest -m unit -v

# Run integration tests
pytest -m integration -v
```

### Marker Definition (pytest.ini)
```ini
markers =
    unit: Unit tests (isolated functionality)
    integration: Integration tests (component interaction)
    api: API endpoint tests
    e2e: End-to-end tests (full workflows)
    security: Security and authentication tests
    critical: Critical path tests
    edge_case: Edge case tests
    slow: Slow tests (skip with -m "not slow")
```

---

## 🛠️ Configuration Files

### pytest.ini
Main pytest configuration:
```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --color=yes --alluredir=tests/reports/allure-results
testpaths = tests
```

### tests/conftest.py
Global fixtures and hooks:
```python
@pytest.fixture
def logger_fixture():
    """Logger for tests"""
    return logging.getLogger("pytest")

@pytest.fixture
def test_report_dir():
    """Test report directory"""
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    return report_dir
```

---

## 📊 Test Results

### Expected Results
```
✅ 91+ tests PASSING (100%)
✅ Coverage: 70%+
✅ Pass Rate: 98%+
✅ No critical failures
```

### Results Location
```
tests/reports/
├── allure-results/          # Raw test results (Allure format)
├── allure-report/           # Generated HTML report
├── test_execution.log       # Full pytest log
└── pytest.log               # Test framework log
```

---

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests with Allure Report

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.12
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest allure-pytest
      
      - name: Run tests
        run: python3 test_runner.py
      
      - name: Upload Allure report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: allure-report
          path: tests/reports/allure-report/
```

---

## 🔍 Troubleshooting

### Allure Not Installed
```bash
# Install Allure
npm install -g allure-commandline

# Or via pip
pip install allure-pytest
```

### JWT_SECRET_KEY Not Set
```bash
# Error: ValueError: JWT_SECRET_KEY environment variable not set!

# Fix:
export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

### Encryption Key Not Set
```bash
# Error: Encryption not available

# Fix:
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### Report Not Generated
```bash
# Check test results exist
ls -la tests/reports/allure-results/

# Manually generate
allure generate tests/reports/allure-results --clean -o tests/reports/allure-report/
```

---

## 📋 Checklist

### Before Running Tests
- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Allure installed: `npm install -g allure-commandline` or `pip install allure-pytest`

### Running Tests
- [ ] Execute: `python3 test_runner.py`
- [ ] Wait for tests to complete (usually <10 seconds)
- [ ] Check results: ✅ All tests pass

### After Tests
- [ ] View report: Open `tests/reports/allure-report/index.html`
- [ ] Review statistics
- [ ] Check for failures
- [ ] Archive results if needed

---

## 💡 Best Practices

### For Development
```bash
# Run tests frequently during development
python3 test_runner.py

# Run specific test file while developing
pytest tests/unit/test_auth.py -v

# Run tests in watch mode
pytest-watch tests/unit/ -v
```

### For CI/CD
```bash
# Run in CI/CD with exit code
python3 test_runner.py || exit 1

# Generate report for artifacts
allure serve tests/reports/allure-results
```

### For Debugging
```bash
# Show print statements
pytest tests/unit/ -s -v

# Show local variables on failure
pytest tests/unit/ --tb=long -v

# Stop at first failure
pytest tests/unit/ -x -v

# Show slow tests
pytest tests/unit/ --durations=10 -v
```

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Allure Report Documentation](https://docs.qameta.io/allure/)
- [Python Unittest Best Practices](https://docs.python.org/3/library/unittest.html)

---

## 🎯 Summary

This automated test runner provides:
- ✅ Easy one-command test execution
- ✅ Professional Allure reports
- ✅ Environment variable management
- ✅ Comprehensive test coverage
- ✅ CI/CD ready configuration
- ✅ Beautiful HTML reports

**Status**: Ready for Production Use! 🚀

