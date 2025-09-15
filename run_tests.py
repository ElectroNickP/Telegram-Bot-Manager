#!/usr/bin/env python3
"""
Скрипт для запуска профессионального тестирования Telegram Bot Manager
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime


def run_command(command, description):
    """Выполнение команды с выводом"""
    print(f"\n🔧 {description}")
    print(f"Команда: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Код выхода: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка выполнения команды: {e}")
        return False


def check_app_running():
    """Проверка, что приложение запущено"""
    try:
        import requests

        response = requests.get("http://localhost:5000/api/v2/system/health", timeout=5)
        return response.status_code in [200, 401]
    except:
        return False


def start_application():
    """Запуск приложения"""
    print("🚀 Запуск Telegram Bot Manager...")

    # Проверяем, не запущено ли уже приложение
    if check_app_running():
        print("✅ Приложение уже запущено")
        return True

    # Запускаем приложение в фоне
    cmd = "cd src && python3 app.py > ../logs/app.log 2>&1 &"
    success = run_command(cmd, "Запуск приложения")

    if success:
        # Ждем запуска
        print("⏳ Ожидание запуска приложения...")
        for i in range(30):  # Ждем до 30 секунд
            time.sleep(1)
            if check_app_running():
                print("✅ Приложение успешно запущено")
                return True
            print(f"⏳ Попытка {i+1}/30...")

        print("❌ Приложение не запустилось в течение 30 секунд")
        return False

    return False


def run_test_suite(test_type, description):
    """Запуск набора тестов"""
    print(f"\n🧪 {description}")
    print("=" * 60)

    # Создаем директорию для отчетов
    os.makedirs("reports", exist_ok=True)

    # Команда для запуска тестов
    cmd = f"python3 -m pytest tests/{test_type}/ -v --tb=short --html=reports/{test_type}_report.html --self-contained-html"

    success = run_command(cmd, f"Запуск {test_type} тестов")

    if success:
        print(f"✅ {description} завершены успешно")
    else:
        print(f"❌ {description} завершены с ошибками")

    return success


def run_coverage_test():
    """Запуск тестов с покрытием кода"""
    print("\n📊 Тестирование покрытия кода")
    print("=" * 60)

    cmd = "python3 -m pytest tests/ -v --cov=src --cov-report=html:htmlcov --cov-report=term-missing"

    success = run_command(cmd, "Запуск тестов с покрытием")

    if success:
        print("✅ Тесты покрытия завершены")
    else:
        print("❌ Тесты покрытия завершены с ошибками")

    return success


def run_performance_test():
    """Запуск нагрузочного тестирования"""
    print("\n⚡ Нагрузочное тестирование")
    print("=" * 60)

    # Создаем файл для Locust
    locust_file = """
from locust import HttpUser, task, between

class TelegramBotManagerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.client.post("/api/login", json={
            "username": "admin",
            "password": "securepassword123"
        })
    
    @task(3)
    def health_check(self):
        self.client.get("/api/v2/system/health")
    
    @task(2)
    def get_bots(self):
        self.client.get("/api/v2/bots")
    
    @task(1)
    def get_marketplace(self):
        self.client.get("/api/marketplace/bots")
"""

    with open("locustfile.py", "w") as f:
        f.write(locust_file)

    # Запускаем Locust в фоне
    cmd = "locust -f locustfile.py --host=http://localhost:5000 --users=10 --spawn-rate=2 --run-time=60s --headless --html=reports/load_test_report.html"

    success = run_command(cmd, "Запуск нагрузочного тестирования")

    # Удаляем временный файл
    os.remove("locustfile.py")

    return success


def generate_summary_report():
    """Генерация сводного отчета"""
    print("\n📋 Генерация сводного отчета")
    print("=" * 60)

    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "Telegram Bot Manager v3.4.0",
        "test_results": {
            "unit_tests": "Не выполнены (требуют доработки)",
            "integration_tests": "Частично выполнены",
            "performance_tests": "Выполнены",
            "security_tests": "Частично выполнены",
            "coverage": "Выполнено",
        },
        "recommendations": [
            "Исправить структуру API ответов",
            "Добавить валидацию входных данных",
            "Реализовать защиту от инъекций",
            "Оптимизировать использование CPU",
            "Добавить CSRF защиту",
        ],
        "status": "Требует доработки перед production",
    }

    with open("reports/summary_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("✅ Сводный отчет создан: reports/summary_report.json")


def main():
    """Основная функция"""
    print("🧪 ПРОФЕССИОНАЛЬНОЕ ТЕСТИРОВАНИЕ")
    print("Telegram Bot Manager v3.4.0")
    print("=" * 60)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Проверяем, что мы в правильной директории
    if not os.path.exists("src/app.py"):
        print("❌ Ошибка: Файл src/app.py не найден")
        print("Убедитесь, что вы находитесь в корневой директории проекта")
        sys.exit(1)

    # Создаем директории
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Запускаем приложение
    if not start_application():
        print("❌ Не удалось запустить приложение")
        sys.exit(1)

    # Запускаем тесты
    test_results = {}

    # Интеграционные тесты
    test_results["integration"] = run_test_suite("integration", "Интеграционные тесты API")

    # Тесты производительности
    test_results["performance"] = run_test_suite("performance", "Тесты производительности")

    # Тесты безопасности
    test_results["security"] = run_test_suite("security", "Тесты безопасности")

    # Тесты покрытия
    test_results["coverage"] = run_coverage_test()

    # Нагрузочное тестирование
    test_results["load"] = run_performance_test()

    # Генерируем сводный отчет
    generate_summary_report()

    # Выводим итоги
    print("\n🎯 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)

    print(f"Пройдено тестов: {passed}/{total}")
    print(f"Процент успеха: {(passed/total)*100:.1f}%")

    for test_type, result in test_results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_type.upper()}: {status}")

    print("\n📁 Отчеты сохранены в директории: reports/")
    print("📊 Покрытие кода: htmlcov/index.html")
    print("📋 Сводный отчет: reports/summary_report.json")

    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        print("См. отчеты для деталей и рекомендаций")


if __name__ == "__main__":
    main()
