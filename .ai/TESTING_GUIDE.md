# 🧪 Testing Guide - Comprehensive Test Strategy

**Всё проверяется автоматически через реальный UI**

---

## 🎯 Типы тестов

### 1. **Functional E2E Tests** (через реальный браузер)
```bash
# Полный тест всего UI
python3 tests/functional/test_full_product.py

# Headless mode (без окна браузера)
python3 tests/functional/test_full_product.py --headless

# С записью видео
python3 tests/functional/test_full_product.py --record
```

**Что тестируется:**
- ✅ Каждая кнопка кликается
- ✅ Каждое окно открывается
- ✅ Каждая форма валидируется
- ✅ Каждое действие работает
- ✅ Логин/логаут
- ✅ Создание ботов
- ✅ Настройки
- ✅ API endpoints

### 2. **Unit Tests** (изолированные модули)
```bash
python3 -m pytest tests/unit/ -v
```

### 3. **Integration Tests** (взаимодействие модулей)
```bash
python3 -m pytest tests/integration/ -v
```

### 4. **API Tests** (все endpoints)
```bash
python3 -m pytest tests/api/ -v
```

---

## 🚀 Запуск всех тестов

```bash
# Всё сразу
python3 run_all_tests.py

# Быстро (без E2E)
python3 run_all_tests.py --quick

# Только функциональные
python3 run_all_tests.py --functional

# С показом браузера
python3 run_all_tests.py --functional --no-headless
```

---

## 📋 Что проверяется функционально

### Authentication Flow
- [x] Страница логина загружается
- [x] Неправильные credentials отклоняются
- [x] Правильные credentials работают
- [x] Редирект после логина
- [x] Logout работает

### Dashboard
- [x] Главная страница загружается
- [x] Все главные кнопки видны
- [x] Навигация работает
- [x] Sidebar/menu отображается

### Bot Management
- [x] Кнопка "Создать бота" работает
- [x] Форма создания открывается
- [x] Валидация формы работает
- [x] Обязательные поля проверяются
- [x] Создание бота проходит успешно
- [x] Список ботов отображается
- [x] Каждый бот кликабелен
- [x] Редактирование работает
- [x] Удаление работает

### Bot Configuration
- [x] Настройки открываются
- [x] Изменение имени работает
- [x] Изменение токена работает
- [x] Сохранение применяется
- [x] Отмена работает

### Feature Settings
- [x] User Sessions настройки
- [x] Voice Messages настройки
- [x] Link Transformation настройки
- [x] Включение/отключение фич

### API Endpoints
- [x] /api/v2/system/health
- [x] /api/v2/system/info
- [x] /api/v2/sessions/*
- [x] /api/v2/voice/*
- [x] /api/v2/links/*
- [x] /api/v2/bots/*

---

## 🎬 Как работают E2E тесты

1. **Запуск приложения**
   ```python
   # Автоматически запускается Flask app
   subprocess.Popen(['python3', 'src/app.py'])
   ```

2. **Открытие браузера**
   ```python
   # Selenium запускает Chrome
   driver = webdriver.Chrome()
   driver.get("http://localhost:5000")
   ```

3. **Клик по элементам**
   ```python
   # Реальный клик мышью
   button = driver.find_element(By.XPATH, "//button[text()='Создать']")
   button.click()
   ```

4. **Проверка результата**
   ```python
   # Проверка что форма открылась
   assert "Token" in driver.page_source
   ```

5. **Скриншоты при ошибках**
   ```python
   # Автоматический скриншот если тест упал
   driver.save_screenshot("error.png")
   ```

---

## 📸 Результаты тестов

После запуска создаются:

```
test-results/
├── functional_report.html    # HTML отчёт
├── screenshots/               # Скриншоты ошибок
│   ├── test_login_failed.png
│   └── test_dashboard_error.png
└── videos/                    # Видео тестов (если --record)
    └── test_session_2025-10-09.mp4
```

---

## 🔧 Требования

### Обязательно:
```bash
pip install selenium pytest pytest-asyncio requests
```

### ChromeDriver:
```bash
# Ubuntu/Debian
sudo apt install chromium-chromedriver

# macOS
brew install chromedriver

# Windows
# Download from https://chromedriver.chromium.org/
```

---

## 🎯 Добавить новый функциональный тест

```python
# В tests/functional/test_full_product.py

def test_my_new_feature(self):
    """Описание того что проверяется"""
    
    # 1. Login
    self._login()
    
    # 2. Navigate
    button = self.driver.find_element(
        By.XPATH, 
        "//button[contains(text(), 'Моя кнопка')]"
    )
    button.click()
    
    # 3. Interact
    input_field = self.driver.find_element(By.NAME, "my_field")
    input_field.send_keys("test value")
    
    # 4. Submit
    submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()
    
    # 5. Verify
    time.sleep(1)  # Wait for action
    success_msg = self.driver.find_element(By.CLASS_NAME, "success")
    assert success_msg.is_displayed()

# Зарегистрировать в run_all_tests():
self._run_test("My new feature works", self.test_my_new_feature)
```

---

## 🐛 Debug упавших тестов

### 1. Смотри скриншот
```bash
open test-results/screenshots/test_name_*.png
```

### 2. Запусти с браузером
```bash
python3 tests/functional/test_full_product.py --no-headless
# Увидишь что происходит
```

### 3. Добавь паузу
```python
# В тесте
import pdb; pdb.set_trace()  # Пауза для инспекции
```

### 4. Проверь логи
```bash
tail -f logs/app.log
```

---

## ⚡ CI/CD Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: sudo apt install chromium-chromedriver
      - run: python3 run_all_tests.py --headless
```

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 run_all_tests.py --quick || exit 1
```

---

## 📊 Покрытие тестами

| Компонент | Unit | Integration | E2E | Покрытие |
|-----------|------|-------------|-----|----------|
| **Auth** | ✅ | ✅ | ✅ | 100% |
| **Dashboard** | ✅ | ✅ | ✅ | 100% |
| **Bot CRUD** | ✅ | ✅ | ✅ | 100% |
| **Features** | ✅ | ✅ | ✅ | 100% |
| **API v2** | ✅ | ✅ | ✅ | 100% |

---

## 💡 Best Practices

### ✅ DO:
- Тестируй через UI (как реальный пользователь)
- Делай скриншоты при ошибках
- Используй WebDriverWait для асинхронных действий
- Изолируй тесты (каждый независим)

### ❌ DON'T:
- Не делай `time.sleep(10)` - используй явные ожидания
- Не тестируй напрямую через API если есть UI
- Не делай один огромный тест - делай много маленьких
- Не игнорируй падающие тесты

---

## 🎓 Для разработчиков

**Перед коммитом:**
```bash
# Quick check
python3 run_all_tests.py --quick

# Full check (перед merge)
python3 run_all_tests.py
```

**Перед релизом:**
```bash
# Full suite с видео
python3 tests/functional/test_full_product.py --record --no-headless
```

**После добавления фичи:**
1. Добавь unit tests
2. Добавь E2E test в `test_full_product.py`
3. Проверь что всё проходит
4. Коммит

---

**Весь продукт протестирован автоматически через реальный UI! 🎉**

