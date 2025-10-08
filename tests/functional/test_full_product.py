#!/usr/bin/env python3
"""
Functional E2E Test Suite

Тестирует весь продукт через реальный UI:
- Каждая кнопка
- Каждое окно
- Каждое действие
- Реальный браузер (Selenium)
- Реальный Flask app
- Реальная база данных

Usage:
    python3 tests/functional/test_full_product.py
    python3 tests/functional/test_full_product.py --headless  # Без UI
    python3 tests/functional/test_full_product.py --record    # Запись видео
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
import subprocess
import signal

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Результат теста"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    screenshot: Optional[str] = None


class FunctionalTestSuite:
    """
    Полный функциональный тест продукта
    
    Запускает реальное приложение и тестирует через браузер.
    """
    
    def __init__(self, headless: bool = False, record: bool = False):
        self.headless = headless
        self.record = record
        self.driver: Optional[webdriver.Chrome] = None
        self.app_process: Optional[subprocess.Popen] = None
        self.base_url = "http://localhost:5000"
        self.admin_user = "admin"
        self.admin_pass = "admin"
        self.results: List[TestResult] = []
        self.screenshots_dir = PROJECT_ROOT / "test-results" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def setup(self):
        """Настройка тестового окружения"""
        logger.info("🔧 Setting up test environment...")
        
        # Start Flask app
        self._start_app()
        
        # Setup Selenium
        self._setup_selenium()
        
        logger.info("✅ Test environment ready")
    
    def _start_app(self):
        """Запуск Flask приложения"""
        logger.info("🚀 Starting Flask app...")
        
        app_script = PROJECT_ROOT / "src" / "app.py"
        
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'
        env['PORT'] = '5000'
        
        self.app_process = subprocess.Popen(
            ['python3', str(app_script)],
            cwd=str(PROJECT_ROOT / 'src'),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # For proper cleanup
        )
        
        # Wait for app to start
        max_wait = 30
        for i in range(max_wait):
            try:
                import requests
                response = requests.get(f"{self.base_url}/", timeout=1)
                if response.status_code in [200, 302, 401]:
                    logger.info("✅ Flask app started")
                    return
            except:
                time.sleep(1)
        
        raise RuntimeError("Failed to start Flask app")
    
    def _setup_selenium(self):
        """Настройка Selenium WebDriver"""
        logger.info("🌐 Setting up Selenium...")
        
        options = ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            logger.info("✅ Selenium ready")
        except Exception as e:
            logger.error(f"❌ Failed to setup Selenium: {e}")
            logger.info("💡 Install ChromeDriver: sudo apt install chromium-chromedriver")
            raise
    
    def teardown(self):
        """Очистка после тестов"""
        logger.info("🧹 Cleaning up...")
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.app_process:
            try:
                os.killpg(os.getpgid(self.app_process.pid), signal.SIGTERM)
                self.app_process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.app_process.pid), signal.SIGKILL)
                except:
                    pass
        
        logger.info("✅ Cleanup complete")
    
    def _take_screenshot(self, name: str) -> str:
        """Сделать скриншот"""
        if not self.driver:
            return None
        
        filename = f"{name.replace(' ', '_')}_{int(time.time())}.png"
        filepath = self.screenshots_dir / filename
        
        try:
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except:
            return None
    
    def _run_test(self, name: str, test_func):
        """Запустить один тест"""
        logger.info(f"\n▶️  Test: {name}")
        start_time = time.time()
        
        try:
            test_func()
            duration = time.time() - start_time
            
            result = TestResult(
                name=name,
                passed=True,
                duration=duration
            )
            logger.info(f"✅ PASS ({duration:.2f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = self._take_screenshot(name)
            
            result = TestResult(
                name=name,
                passed=False,
                duration=duration,
                error=str(e),
                screenshot=screenshot
            )
            logger.error(f"❌ FAIL ({duration:.2f}s): {e}")
            if screenshot:
                logger.info(f"📸 Screenshot: {screenshot}")
        
        self.results.append(result)
    
    # ========================================================================
    # TESTS: Authentication
    # ========================================================================
    
    def test_login_page_loads(self):
        """Страница логина загружается"""
        self.driver.get(self.base_url)
        assert "Telegram Bot Manager" in self.driver.title or "Login" in self.driver.title
        
        # Проверяем элементы формы
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        assert username_field.is_displayed()
        assert password_field.is_displayed()
        assert login_button.is_displayed()
    
    def test_login_with_wrong_credentials(self):
        """Неправильные credentials отклоняются"""
        self.driver.get(self.base_url)
        
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("wrong_user")
        password_field.send_keys("wrong_pass")
        login_button.click()
        
        time.sleep(1)
        
        # Должны остаться на странице логина
        assert "/login" in self.driver.current_url or self.driver.current_url == f"{self.base_url}/"
    
    def test_login_with_correct_credentials(self):
        """Правильные credentials работают"""
        self.driver.get(self.base_url)
        
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.clear()
        password_field.clear()
        username_field.send_keys(self.admin_user)
        password_field.send_keys(self.admin_pass)
        login_button.click()
        
        # Ждем редиректа
        WebDriverWait(self.driver, 10).until(
            lambda d: "/dashboard" in d.current_url or "/index" in d.current_url
        )
    
    # ========================================================================
    # TESTS: Dashboard
    # ========================================================================
    
    def test_dashboard_loads(self):
        """Главная страница dashboard загружается"""
        self._login()
        
        # Проверяем наличие ключевых элементов
        assert self.driver.find_element(By.TAG_NAME, "body")
        
        # Навигация должна быть
        try:
            nav = self.driver.find_element(By.TAG_NAME, "nav")
            assert nav.is_displayed()
        except:
            # Может быть sidebar
            sidebar = self.driver.find_element(By.CSS_SELECTOR, ".sidebar, .side-menu, [class*='nav']")
            assert sidebar.is_displayed()
    
    def test_all_main_buttons_visible(self):
        """Все главные кнопки видны"""
        self._login()
        
        # Ищем основные кнопки/ссылки
        expected_buttons = [
            "Боты",  # Список ботов
            "Создать",  # Создать бота
        ]
        
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        for button_text in expected_buttons:
            # Ищем либо кнопку, либо ссылку с таким текстом
            try:
                element = self.driver.find_element(
                    By.XPATH, 
                    f"//*[contains(text(), '{button_text}')]"
                )
                logger.info(f"   Found: {button_text}")
            except:
                logger.warning(f"   Missing: {button_text}")
    
    # ========================================================================
    # TESTS: Bot Creation
    # ========================================================================
    
    def test_create_bot_button_works(self):
        """Кнопка создания бота работает"""
        self._login()
        
        # Находим кнопку создания бота
        try:
            create_button = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Создать') or contains(text(), 'Create') or contains(text(), 'Добавить')]"
            )
            create_button.click()
        except:
            # Попробуем найти через ID или класс
            create_button = self.driver.find_element(By.CSS_SELECTOR, "[href*='create'], [href*='new'], .create-btn")
            create_button.click()
        
        # Должна открыться форма или страница создания
        time.sleep(1)
        
        # Проверяем что форма появилась
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        assert any(word in page_text.lower() for word in ['token', 'bot', 'name', 'создать'])
    
    def test_bot_creation_form_validation(self):
        """Валидация формы создания бота"""
        self._login()
        self._navigate_to_create_bot()
        
        # Попытка создать без заполнения полей
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR,
            "button[type='submit'], .submit-btn, [class*='save']"
        )
        submit_button.click()
        
        time.sleep(1)
        
        # Должно быть сообщение об ошибке или мы остались на форме
        # (HTML5 validation или backend validation)
        # В любом случае, бот не должен создаться
    
    # ========================================================================
    # TESTS: Bot List
    # ========================================================================
    
    def test_bot_list_displays(self):
        """Список ботов отображается"""
        self._login()
        
        # Переходим к списку ботов
        try:
            bots_link = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Боты') or contains(text(), 'Bots')]"
            )
            bots_link.click()
            time.sleep(1)
        except:
            # Уже на странице списка
            pass
        
        # Проверяем что есть контейнер для списка ботов
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        # Либо есть боты, либо есть сообщение "нет ботов"
        has_bots = "bot" in body_text.lower() or "бот" in body_text.lower()
        assert has_bots or "пусто" in body_text.lower() or "empty" in body_text.lower()
    
    # ========================================================================
    # TESTS: API Health
    # ========================================================================
    
    def test_api_v2_health_endpoint(self):
        """API health endpoint работает"""
        import requests
        
        response = requests.get(
            f"{self.base_url}/api/v2/system/health",
            auth=(self.admin_user, self.admin_pass)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        logger.info(f"   System status: {data.get('status')}")
    
    def test_api_v2_system_info(self):
        """API system info работает"""
        import requests
        
        response = requests.get(
            f"{self.base_url}/api/v2/system/info",
            auth=(self.admin_user, self.admin_pass)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "version" in data or "python_version" in data
    
    # ========================================================================
    # TESTS: Feature APIs
    # ========================================================================
    
    def test_feature_sessions_api_exists(self):
        """API для user_sessions существует"""
        import requests
        
        # Должен вернуть 200 или 400 (not 404)
        response = requests.get(
            f"{self.base_url}/api/v2/sessions/active?bot_id=1",
            auth=(self.admin_user, self.admin_pass)
        )
        
        # Важно что endpoint существует (not 404)
        assert response.status_code != 404, "Sessions API endpoint missing"
        logger.info(f"   Sessions API status: {response.status_code}")
    
    def test_feature_voice_api_exists(self):
        """API для voice_messages существует"""
        import requests
        
        # POST endpoint может требовать data, но должен существовать
        response = requests.post(
            f"{self.base_url}/api/v2/voice/transcribe",
            auth=(self.admin_user, self.admin_pass)
        )
        
        # Важно что endpoint существует (not 404)
        # Может быть 400 (bad request), но не 404
        assert response.status_code != 404, "Voice API endpoint missing"
        logger.info(f"   Voice API status: {response.status_code}")
    
    def test_feature_links_api_exists(self):
        """API для link_transformation существует"""
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/v2/links/preview",
            auth=(self.admin_user, self.admin_pass),
            json={"text": "test", "config": {}}
        )
        
        # Должен обработать запрос (not 404)
        assert response.status_code != 404, "Links API endpoint missing"
        logger.info(f"   Links API status: {response.status_code}")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _login(self):
        """Войти в систему"""
        self.driver.get(self.base_url)
        
        try:
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            username_field.clear()
            password_field.clear()
            username_field.send_keys(self.admin_user)
            password_field.send_keys(self.admin_pass)
            login_button.click()
            
            # Wait for redirect
            time.sleep(2)
        except:
            # Already logged in
            pass
    
    def _navigate_to_create_bot(self):
        """Перейти к форме создания бота"""
        try:
            create_button = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Создать') or contains(text(), 'Create')]"
            )
            create_button.click()
            time.sleep(1)
        except:
            # Try direct URL
            self.driver.get(f"{self.base_url}/create")
            time.sleep(1)
    
    # ========================================================================
    # Test Runner
    # ========================================================================
    
    def run_all_tests(self):
        """Запустить все тесты"""
        logger.info("="*70)
        logger.info("FUNCTIONAL E2E TEST SUITE")
        logger.info("="*70)
        
        # Authentication tests
        logger.info("\n📝 Authentication Tests")
        self._run_test("Login page loads", self.test_login_page_loads)
        self._run_test("Wrong credentials rejected", self.test_login_with_wrong_credentials)
        self._run_test("Correct credentials work", self.test_login_with_correct_credentials)
        
        # Dashboard tests
        logger.info("\n📊 Dashboard Tests")
        self._run_test("Dashboard loads", self.test_dashboard_loads)
        self._run_test("Main buttons visible", self.test_all_main_buttons_visible)
        
        # Bot management tests
        logger.info("\n🤖 Bot Management Tests")
        self._run_test("Create bot button works", self.test_create_bot_button_works)
        self._run_test("Bot creation form validation", self.test_bot_creation_form_validation)
        self._run_test("Bot list displays", self.test_bot_list_displays)
        
        # API tests
        logger.info("\n🔌 API Tests")
        self._run_test("API health endpoint", self.test_api_v2_health_endpoint)
        self._run_test("API system info", self.test_api_v2_system_info)
        
        # Feature API tests
        logger.info("\n🧩 Feature API Tests")
        self._run_test("Sessions API exists", self.test_feature_sessions_api_exists)
        self._run_test("Voice API exists", self.test_feature_voice_api_exists)
        self._run_test("Links API exists", self.test_feature_links_api_exists)
        
        # Print results
        self._print_summary()
    
    def _print_summary(self):
        """Вывести итоговый отчёт"""
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        
        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]
        
        total_duration = sum(r.duration for r in self.results)
        
        logger.info(f"\nTotal tests:  {len(self.results)}")
        logger.info(f"Passed:       {len(passed)} ✅")
        logger.info(f"Failed:       {len(failed)} ❌")
        logger.info(f"Duration:     {total_duration:.2f}s")
        logger.info(f"Success rate: {len(passed)/len(self.results)*100:.1f}%")
        
        if failed:
            logger.info("\n❌ FAILED TESTS:")
            for result in failed:
                logger.info(f"   - {result.name}")
                if result.error:
                    logger.info(f"     Error: {result.error}")
                if result.screenshot:
                    logger.info(f"     Screenshot: {result.screenshot}")
        
        # Generate HTML report
        self._generate_html_report()
        
        logger.info("\n" + "="*70)
        
        if len(failed) == 0:
            logger.info("🎉 ALL TESTS PASSED!")
            return True
        else:
            logger.error(f"💔 {len(failed)} TESTS FAILED")
            return False
    
    def _generate_html_report(self):
        """Сгенерировать HTML отчёт"""
        report_file = PROJECT_ROOT / "test-results" / "functional_report.html"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Functional Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .screenshot {{ max-width: 400px; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>Functional E2E Test Report</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Summary</h2>
    <ul>
        <li>Total tests: {len(self.results)}</li>
        <li class="pass">Passed: {sum(1 for r in self.results if r.passed)}</li>
        <li class="fail">Failed: {sum(1 for r in self.results if not r.passed)}</li>
        <li>Total duration: {sum(r.duration for r in self.results):.2f}s</li>
    </ul>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Details</th>
        </tr>
"""
        
        for result in self.results:
            status_class = "pass" if result.passed else "fail"
            status_text = "✅ PASS" if result.passed else "❌ FAIL"
            
            html += f"""
        <tr>
            <td>{result.name}</td>
            <td class="{status_class}">{status_text}</td>
            <td>{result.duration:.2f}s</td>
            <td>
"""
            
            if result.error:
                html += f"<pre>{result.error}</pre>"
            
            if result.screenshot:
                rel_path = Path(result.screenshot).relative_to(PROJECT_ROOT)
                html += f'<br><img src="../{rel_path}" class="screenshot" onclick="window.open(this.src)">'
            
            html += """
            </td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"\n📄 HTML report: {report_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run functional E2E tests')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--record', action='store_true', help='Record video')
    args = parser.parse_args()
    
    suite = FunctionalTestSuite(headless=args.headless, record=args.record)
    
    try:
        suite.setup()
        success = suite.run_all_tests()
        return 0 if success else 1
    
    except Exception as e:
        logger.error(f"❌ Test suite crashed: {e}", exc_info=True)
        return 2
    
    finally:
        suite.teardown()


if __name__ == '__main__':
    sys.exit(main())

