#!/usr/bin/env python3
"""
AI Onboarding Tool

Быстрый старт для любого AI:
- Показывает структуру проекта
- Текущий статус
- Что нужно сделать
- Quick commands

Usage:
    python3 .ai/tools/ai-onboard.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_live_context():
    """Загрузить актуальный контекст"""
    context_file = PROJECT_ROOT / '.ai' / 'LIVE_CONTEXT.json'
    if context_file.exists():
        with open(context_file, 'r') as f:
            return json.load(f)
    return {}

def load_coverage():
    """Загрузить coverage данные"""
    coverage_file = PROJECT_ROOT / '.ai' / 'TEST_COVERAGE.json'
    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            return json.load(f)
    return {}

def print_banner():
    """Красивый баннер"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 AI ONBOARDING - Быстрый старт                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

def show_project_info():
    """Показать информацию о проекте"""
    print("📦 ПРОЕКТ: Telegram Bot Manager")
    print("📝 Описание: Multi-bot управление с AI, голосом, сессиями")
    print("🏗️  Архитектура: Hexagonal (Ports & Adapters) + Feature-based")
    print("🧪 Тестирование: Auto-gen + Coverage tracking")
    print("")

def show_structure(context):
    """Показать структуру"""
    if not context:
        print("⚠️  Context не найден, запусти: python3 .ai/tools/validate-context.py --generate")
        return
    
    structure = context.get('project_structure', {})
    features = structure.get('features', [])
    
    print("🏗️  СТРУКТУРА:")
    print(f"   Features: {len(features)}")
    for feature in features:
        print(f"      ✅ {feature}")
    
    print(f"   Core modules: {len(structure.get('core_modules', []))}")
    print(f"   API versions: {len(structure.get('api_modules', []))}")
    print("")

def show_coverage(coverage):
    """Показать coverage"""
    if not coverage:
        print("⚠️  Coverage не найден, запусти: python3 .ai/tools/auto-test-gen.py")
        return
    
    cov = coverage.get('coverage', {})
    total = cov.get('total', 0)
    tested = cov.get('tested', 0)
    percentage = cov.get('percentage', 0)
    
    print("🧪 TEST COVERAGE:")
    print(f"   Overall: {tested}/{total} ({percentage}%)")
    
    by_priority = coverage.get('by_priority', {})
    if by_priority:
        print("   По приоритетам:")
        for priority in sorted(by_priority.keys(), reverse=True):
            data = by_priority[priority]
            pct = (data['tested'] / data['total'] * 100) if data['total'] > 0 else 0
            priority_name = {5: 'CRITICAL', 4: 'HIGH', 3: 'MEDIUM', 2: 'LOW', 1: 'TRIVIAL'}[int(priority)]
            status = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "🔥"
            print(f"      {status} Priority {priority} ({priority_name}): {data['tested']}/{data['total']} ({pct:.1f}%)")
    
    print("")

def show_quick_commands():
    """Показать быстрые команды"""
    print("⚡ QUICK COMMANDS:")
    print("""
   # Проверить статус проекта
   python3 .ai/tools/ai-status.py
   
   # Обновить context
   python3 .ai/tools/validate-context.py --generate
   
   # Проанализировать coverage
   python3 .ai/tools/auto-test-gen.py
   
   # Сгенерировать тесты для критичного кода
   python3 .ai/tools/auto-test-gen.py --generate
   
   # Запустить все тесты
   python3 run_all_tests.py
   
   # Быстрые тесты (без E2E)
   python3 run_all_tests.py --quick
   
   # Запустить проект
   python3 start.py
""")

def show_critical_todos():
    """Показать критичные TODO"""
    print("🔥 КРИТИЧНЫЕ ЗАДАЧИ:")
    print("""
   1. Улучшить coverage до 70%+
      - Focus: Critical entities (45)
      - Priority: HIGH
      
   2. Протестировать E2E
      - Требует: Flask running
      - Priority: MEDIUM
      
   3. Phase 3-8 Production Plan
      - UI Password Change
      - Auto-Update UI
      - Auto-Backup System
""")
    print("")

def show_ai_instructions():
    """Показать инструкции для AI"""
    print("🤖 ИНСТРУКЦИИ ДЛЯ AI:")
    print("""
   1. ВСЕГДА читай .ai/LIVE_CONTEXT.json перед работой
   2. ВСЕГДА генерируй тесты для нового кода
   3. ВСЕГДА проверяй coverage после изменений
   4. ВСЕГДА коммить через git (hooks сделают всё)
   5. ВСЕГДА запускай ai-validate.py перед push
   
   📖 Подробнее: .ai/AI_DRIVEN_DEV.md
""")

def show_health_status():
    """Показать статус здоровья"""
    # Check critical files
    critical_files = [
        '.ai/LIVE_CONTEXT.json',
        '.ai/TEST_COVERAGE.json',
        'core/features/base.py',
        'core/features/registry.py',
    ]
    
    all_exist = all((PROJECT_ROOT / f).exists() for f in critical_files)
    
    print("💚 HEALTH STATUS:")
    if all_exist:
        print("   ✅ All critical files present")
        print("   ✅ System operational")
    else:
        print("   ⚠️  Some critical files missing")
        print("   → Run: python3 .ai/tools/validate-context.py --generate")
    print("")

def main():
    print_banner()
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Load data
    context = load_live_context()
    coverage = load_coverage()
    
    # Show info
    show_project_info()
    show_health_status()
    show_structure(context)
    show_coverage(coverage)
    show_critical_todos()
    show_quick_commands()
    show_ai_instructions()
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                   🚀 Готов к работе! Good luck!                            ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

if __name__ == '__main__':
    main()

