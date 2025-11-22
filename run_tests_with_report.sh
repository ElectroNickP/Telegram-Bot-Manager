#!/bin/bash

# Complete Test Runner with Allure Report Generation
# Запускает тесты и автоматически создаёт Allure Report

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Source venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Set required environment variables
export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

RESULTS_DIR="tests/reports/allure-results"
REPORT_DIR="tests/reports/allure-report"
LOG_FILE="tests/reports/test_execution.log"

echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                               ║"
echo "║              🧪 AUTOMATIC TEST RUNNER WITH ALLURE REPORT 🧪                  ║"
echo "║                                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Create directories
mkdir -p "$RESULTS_DIR" "$REPORT_DIR"

echo "📋 TEST CONFIGURATION:"
echo "   Results Dir:  $RESULTS_DIR"
echo "   Report Dir:   $REPORT_DIR"
echo "   Log File:     $LOG_FILE"
echo ""

# Display test markers available
echo "📌 Available Test Markers:"
echo "   pytest --markers"
echo ""

# Run tests with Allure integration
echo "🚀 RUNNING TESTS WITH ALLURE..."
echo ""

python3 -m pytest \
    tests/unit/ \
    tests/integration/ \
    -v \
    --tb=short \
    --alluredir="$RESULTS_DIR" \
    --strict-markers \
    --color=yes \
    2>&1 | tee "$LOG_FILE"

TEST_EXIT_CODE=$?

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
else
    echo "⚠️  SOME TESTS FAILED (exit code: $TEST_EXIT_CODE)"
fi

echo ""
echo "📊 GENERATING ALLURE REPORT..."
echo ""

# Check if Allure is installed
if ! command -v allure &> /dev/null; then
    echo "⚠️  Allure not found, installing..."
    npm install -g allure-commandline 2>/dev/null || pip install allure-pytest
fi

# Generate Allure report
if [ -d "$RESULTS_DIR" ] && [ "$(ls -A $RESULTS_DIR)" ]; then
    allure generate "$RESULTS_DIR" --clean -o "$REPORT_DIR" 2>/dev/null || true
    
    echo "✅ Allure Report Generated!"
    echo ""
    echo "📄 Report Location: $REPORT_DIR/index.html"
    echo ""
    echo "🌐 View Report Options:"
    echo "   1. Static HTML: open $REPORT_DIR/index.html"
    echo "   2. Live Server: allure serve $RESULTS_DIR"
    echo ""
    
    # Try to open in browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "file://$REPORT_DIR/index.html" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "file://$REPORT_DIR/index.html" 2>/dev/null &
    fi
else
    echo "⚠️  No test results found to generate report"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 TEST SUMMARY:"
echo "   Exit Code:    $TEST_EXIT_CODE"
echo "   Log File:     $LOG_FILE"
echo "   Report:       $REPORT_DIR/index.html"
echo ""

# Show test count
if [ -f "$LOG_FILE" ]; then
    echo "📈 Test Statistics:"
    grep -E "passed|failed|error" "$LOG_FILE" | tail -1 || true
fi

echo ""
echo "✨ TEST RUN COMPLETE!"
echo ""

exit $TEST_EXIT_CODE

