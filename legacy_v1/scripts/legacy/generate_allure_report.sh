#!/bin/bash

# Allure Report Generator Script
# Автоматически создаёт Allure Report после тестирования

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$PROJECT_ROOT/tests/reports/allure-results"
REPORT_DIR="$PROJECT_ROOT/tests/reports/allure-report"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🧪 Allure Report Generation Started                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Allure is installed
if ! command -v allure &> /dev/null; then
    echo "❌ Allure not found! Installing..."
    npm install -g allure-commandline
fi

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "❌ Error: Results directory not found at $RESULTS_DIR"
    exit 1
fi

# Check if there are test results
if [ -z "$(ls -A $RESULTS_DIR)" ]; then
    echo "⚠️  Warning: No test results found in $RESULTS_DIR"
    echo "Run tests first: pytest --alluredir=$RESULTS_DIR"
    exit 1
fi

echo "📊 Test Results Found:"
echo "   Location: $RESULTS_DIR"
ls -la "$RESULTS_DIR" | tail -5
echo ""

# Generate Allure report
echo "🔨 Generating Allure Report..."
allure generate "$RESULTS_DIR" --clean -o "$REPORT_DIR"

echo ""
echo "✅ Report generated successfully!"
echo "   Location: $REPORT_DIR"
echo ""

# Open report in browser (if available)
if command -v xdg-open &> /dev/null; then
    echo "🌐 Opening report in browser..."
    xdg-open "file://$REPORT_DIR/index.html" &
elif command -v open &> /dev/null; then
    open "file://$REPORT_DIR/index.html"
fi

echo ""
echo "📊 Report ready at: $REPORT_DIR/index.html"
echo ""
echo "Or serve live with:"
echo "   allure serve $RESULTS_DIR"

