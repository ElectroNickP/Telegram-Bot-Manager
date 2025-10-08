#!/usr/bin/env python3
"""
AI Status Tool

Показывает текущий статус проекта для AI:
- System health
- Coverage status
- Pending tasks
- Recommendations

Usage:
    python3 .ai/tools/ai-status.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_coverage():
    """Загрузить coverage"""
    coverage_file = PROJECT_ROOT / '.ai' / 'TEST_COVERAGE.json'
    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            return json.load(f)
    return {}

def check_git_status():
    """Проверить Git статус"""
    try:
        # Uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        uncommitted = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()
        
        return {
            'uncommitted': uncommitted,
            'branch': branch,
            'clean': uncommitted == 0
        }
    except:
        return {'uncommitted': 0, 'branch': 'unknown', 'clean': True}

def check_tests():
    """Проверить тесты"""
    try:
        result = subprocess.run(
            ['python3', '-m', 'pytest', 'tests/', '--collect-only', '-q'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'collected' in line:
                # Extract number
                import re
                match = re.search(r'(\d+) tests? collected', line)
                if match:
                    return {'total': int(match.group(1)), 'status': 'ok'}
        
        return {'total': 0, 'status': 'unknown'}
    except:
        return {'total': 0, 'status': 'error'}

def print_banner():
    """Баннер"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      📊 AI STATUS - Текущее состояние                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

def show_system_health():
    """Показать health"""
    print("💚 SYSTEM HEALTH:")
    
    # Check critical files
    critical_files = {
        'LIVE_CONTEXT.json': '.ai/LIVE_CONTEXT.json',
        'TEST_COVERAGE.json': '.ai/TEST_COVERAGE.json',
        'Feature Base': 'core/features/base.py',
        'Feature Registry': 'core/features/registry.py',
    }
    
    all_ok = True
    for name, path in critical_files.items():
        exists = (PROJECT_ROOT / path).exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name}")
        if not exists:
            all_ok = False
    
    if all_ok:
        print("   → Status: 🟢 GREEN - All systems operational")
    else:
        print("   → Status: 🔴 RED - Critical files missing")
    print("")

def show_coverage_status(coverage):
    """Показать coverage"""
    print("🧪 TEST COVERAGE:")
    
    if not coverage:
        print("   ⚠️  No coverage data. Run: python3 .ai/tools/auto-test-gen.py")
        print("")
        return
    
    cov = coverage.get('coverage', {})
    percentage = cov.get('percentage', 0)
    
    # Overall
    if percentage >= 70:
        status = "🟢 EXCELLENT"
    elif percentage >= 50:
        status = "🟡 GOOD"
    elif percentage >= 30:
        status = "🟠 FAIR"
    else:
        status = "🔴 POOR"
    
    print(f"   Overall: {percentage}% - {status}")
    print(f"   Target: 70%+")
    print(f"   Gap: {max(0, 70 - percentage):.1f}%")
    
    # By priority
    by_priority = coverage.get('by_priority', {})
    if by_priority:
        print("\n   By Priority:")
        for priority in [5, 4, 3, 2, 1]:
            if str(priority) not in by_priority:
                continue
            
            data = by_priority[str(priority)]
            pct = (data['tested'] / data['total'] * 100) if data['total'] > 0 else 0
            
            priority_name = {5: 'CRITICAL', 4: 'HIGH', 3: 'MEDIUM', 2: 'LOW', 1: 'TRIVIAL'}[priority]
            
            if priority == 5:
                target = 100
                status_icon = "✅" if pct >= 100 else "🔥"
            elif priority == 4:
                target = 90
                status_icon = "✅" if pct >= 90 else "⚠️"
            else:
                target = 70
                status_icon = "✅" if pct >= 70 else "💤"
            
            print(f"      {status_icon} P{priority} ({priority_name}): {pct:.1f}% (target: {target}%)")
    
    print("")

def show_git_status(git_info):
    """Показать Git статус"""
    print("📝 GIT STATUS:")
    print(f"   Branch: {git_info['branch']}")
    
    if git_info['clean']:
        print("   Working tree: ✅ Clean")
    else:
        print(f"   Working tree: ⚠️  {git_info['uncommitted']} uncommitted changes")
        print("   → Run: git status")
    
    print("")

def show_test_status(test_info):
    """Показать тест статус"""
    print("🧪 TEST STATUS:")
    
    if test_info['status'] == 'ok':
        print(f"   Tests found: ✅ {test_info['total']}")
        print("   Status: Ready to run")
    elif test_info['status'] == 'error':
        print("   Tests: ❌ Error collecting")
        print("   → Check: pytest tests/ --collect-only")
    else:
        print("   Tests: ⚠️  Unknown status")
    
    print("")

def recommend_next_action(coverage, git_info):
    """Рекомендовать следующее действие"""
    print("🎯 RECOMMENDED NEXT ACTION:")
    
    # Check coverage
    cov = coverage.get('coverage', {})
    percentage = cov.get('percentage', 0)
    
    by_priority = coverage.get('by_priority', {})
    
    # Priority 1: Critical untested
    if by_priority and str(5) in by_priority:
        critical = by_priority[str(5)]
        if critical['tested'] < critical['total']:
            untested = critical['total'] - critical['tested']
            print(f"   🔥 URGENT: {untested} Critical entities need tests!")
            print("   → Run: python3 .ai/tools/auto-test-gen.py --generate")
            print("   → Priority: Tests for Features")
            print("")
            return
    
    # Priority 2: High untested
    if by_priority and str(4) in by_priority:
        high = by_priority[str(4)]
        if high['tested'] < high['total']:
            untested = high['total'] - high['tested']
            print(f"   ⚠️  HIGH: {untested} High-priority entities need tests")
            print("   → Run: python3 .ai/tools/auto-test-gen.py --generate")
            print("")
            return
    
    # Priority 3: Coverage low
    if percentage < 70:
        print(f"   📊 Coverage is {percentage}% (target: 70%)")
        print("   → Focus on: Medium priority entities")
        print("   → Run: python3 .ai/tools/auto-test-gen.py --generate")
        print("")
        return
    
    # Priority 4: Uncommitted changes
    if not git_info['clean']:
        print("   📝 You have uncommitted changes")
        print("   → Review and commit your work")
        print("   → Run: git status")
        print("")
        return
    
    # All good!
    print("   ✅ All systems operational!")
    print("   → You can:")
    print("      - Develop new features")
    print("      - Improve existing code")
    print("      - Run E2E tests")
    print("")

def main():
    print_banner()
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Load data
    coverage = load_coverage()
    git_info = check_git_status()
    test_info = check_tests()
    
    # Show status
    show_system_health()
    show_coverage_status(coverage)
    show_git_status(git_info)
    show_test_status(test_info)
    recommend_next_action(coverage, git_info)
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║              💡 Tip: Run ai-onboard.py for quick start guide               ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

if __name__ == '__main__':
    main()

