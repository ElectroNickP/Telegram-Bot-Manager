# 🧪 TESTING POLICY - Always Up-to-Date

> **Автоматическое покрытие тестами по умолчанию**

---

## 🎯 Политика тестирования

### Правило: **Всё критичное должно быть протестировано**

| Приоритет | Что | Покрытие | Тесты |
|-----------|-----|----------|-------|
| **5 - CRITICAL** | Features | 100% | Unit + Integration + E2E |
| **4 - HIGH** | Use Cases, Domain | 90%+ | Unit + Integration |
| **3 - MEDIUM** | Services, Adapters | 70%+ | Unit |
| **2 - LOW** | Utils, Helpers | 50%+ | Unit |
| **1 - TRIVIAL** | Getters, Setters | Optional | - |

---

## ⚡ Автоматизация (по умолчанию)

### 1. При коммите автоматически:

```bash
git commit -m "feat: my feature"

# Автоматически запускается:
🔍 1. Валидация контекста
📝 2. Обновление meta-файлов
🧪 3. Анализ покрытия
🔧 4. Генерация тестов (для критичного кода)
⚡ 5. Quick tests
```

### 2. Авто-генерация тестов:

```bash
# Анализ покрытия
python3 .ai/tools/auto-test-gen.py

# Генерация недостающих тестов
python3 .ai/tools/auto-test-gen.py --generate

# Только для изменённых файлов
python3 .ai/tools/auto-test-gen.py --diff --generate
```

**Генератор создаёт:**
- ✅ Структуру теста
- ✅ Imports
- ✅ Базовый тест
- ✅ TODO комментарии что дополнить

### 3. Покрытие всегда актуально:

```bash
# Текущее покрытие
cat .ai/TEST_COVERAGE.json

# Детальный отчёт
python3 .ai/tools/auto-test-gen.py
```

---

## 📋 Типы тестов

### 1. **Unit Tests** (изолированно)

**Для чего:** Функции, классы, методы

**Где:** `tests/unit/`

**Пример:**
```python
def test_user_info_creation():
    """Test UserInfo creation"""
    user = UserInfo(
        user_id=123,
        username="test",
        first_name="Test"
    )
    
    assert user.user_id == 123
    assert user.display_name == "Test (@test)"
```

### 2. **Integration Tests** (взаимодействие)

**Для чего:** Use cases, services, взаимодействие компонентов

**Где:** `tests/integration/`

**Пример:**
```python
async def test_session_creation_flow():
    """Test full session creation flow"""
    storage = JsonConfigStorageAdapter()
    use_case = UserSessionManagementUseCase(storage)
    service = UserSessionService(use_case)
    
    # Create session
    session = await service.create_session(...)
    
    assert session.status == SessionStatus.PENDING
    
    # Accept session
    await service.accept_session(...)
    
    assert session.status == SessionStatus.ACTIVE
```

### 3. **E2E Tests** (через UI)

**Для чего:** User flows, UI actions, full scenarios

**Где:** `tests/functional/`

**Пример:**
```python
def test_bot_creation_flow(self):
    """Test creating bot through UI"""
    self._login()
    
    # Click create button
    create_btn = self.driver.find_element(...)
    create_btn.click()
    
    # Fill form
    name_field = self.driver.find_element(...)
    name_field.send_keys("My Bot")
    
    # Submit
    submit_btn = self.driver.find_element(...)
    submit_btn.click()
    
    # Verify created
    assert "My Bot" in self.driver.page_source
```

### 4. **API Tests** (endpoints)

**Для чего:** REST API endpoints

**Где:** `tests/api/`

**Пример:**
```python
def test_health_endpoint():
    """Test /api/v2/system/health"""
    response = requests.get(
        "http://localhost:5000/api/v2/system/health",
        auth=("admin", "admin")
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
```

---

## 🔧 Workflow разработчика

### Добавляешь новую фичу:

```python
# 1. Пишешь код
class MyFeature(Feature):
    def my_method(self):
        return "result"

# 2. Commit
git add src/features/my_feature/
git commit -m "feat: add my_feature"

# Автоматически:
# - Анализируется покрытие
# - Если приоритет HIGH/CRITICAL - генерируется тест
# - Создаётся tests/unit/my_feature/test_feature.py с TODO

# 3. Дополняешь сгенерированный тест
# tests/unit/my_feature/test_feature.py:
def test_my_method():
    """Test my_method"""
    feature = MyFeature()
    result = feature.my_method()
    assert result == "expected"

# 4. Запускаешь тесты
python3 run_all_tests.py --quick

# 5. Commit тестов
git add tests/
git commit -m "test: add tests for my_feature"
```

---

## 📊 Что проверять в тестах

### Unit Tests (изолированно):

- ✅ **Happy path** - нормальный сценарий
- ✅ **Edge cases** - граничные случаи
- ✅ **Error handling** - обработка ошибок
- ✅ **Validation** - валидация входных данных

### Integration Tests (взаимодействие):

- ✅ **Data flow** - данные проходят через слои
- ✅ **Dependencies** - компоненты работают вместе
- ✅ **State changes** - изменения состояния
- ✅ **Transactions** - транзакции (если есть)

### E2E Tests (user flow):

- ✅ **User scenarios** - реальные сценарии пользователя
- ✅ **UI interactions** - кнопки, формы, навигация
- ✅ **Success paths** - успешное выполнение
- ✅ **Error messages** - правильные ошибки

---

## ⚠️ Когда НЕ писать тесты

- ❌ Тривиальные getters/setters (если нет логики)
- ❌ Third-party code (тестируй интеграцию, не сам код)
- ❌ Generated code (если автотесты уже есть)
- ❌ Private helpers (тестируй через public API)

---

## 🎯 Coverage Goals

### Current Status (Live):
```json
{
  "overall": "1.1%",
  "critical": "0%",
  "high": "0%",
  "medium": "1.6%"
}
```

### Target (Progressive):

**Month 1:**
- Critical: 80%
- High: 60%
- Medium: 40%

**Month 2:**
- Critical: 100%
- High: 80%
- Medium: 60%

**Month 3:**
- Critical: 100%
- High: 90%
- Medium: 70%

---

## 🚀 Quick Commands

```bash
# Полный анализ покрытия
python3 .ai/tools/auto-test-gen.py

# Генерация тестов для критичного кода
python3 .ai/tools/auto-test-gen.py --generate

# Генерация только для изменённых файлов
python3 .ai/tools/auto-test-gen.py --diff --generate

# Запуск всех тестов
python3 run_all_tests.py

# Быстрые тесты (без E2E)
python3 run_all_tests.py --quick

# Только unit
python3 -m pytest tests/unit/ -v

# С покрытием
python3 -m pytest tests/unit/ --cov=src --cov-report=html
```

---

## 💡 Best Practices

### ✅ DO:

```python
# Чистые имена тестов
def test_user_creation_with_valid_data():
    """Clear description"""
    pass

# Arrange-Act-Assert
def test_something():
    # Arrange
    user = User(...)
    
    # Act
    result = user.do_something()
    
    # Assert
    assert result == expected

# Параметризация
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6)
])
def test_double(input, expected):
    assert double(input) == expected
```

### ❌ DON'T:

```python
# Плохое имя
def test1():
    pass

# Нет описания
def test_something():
    assert True

# Слишком много в одном тесте
def test_everything():
    # 100 lines of testing...
    pass

# Зависимость между тестами
def test_first():
    global result
    result = do_something()

def test_second():
    assert result == ...  # BAD! Depends on test_first
```

---

## 🔄 CI/CD Integration

### GitHub Actions:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    steps:
      - run: python3 .ai/tools/auto-test-gen.py
      - run: python3 run_all_tests.py
      - name: Check coverage
        run: |
          COVERAGE=$(cat .ai/TEST_COVERAGE.json | jq '.coverage.percentage')
          if (( $(echo "$COVERAGE < 70" | bc -l) )); then
            echo "Coverage too low: $COVERAGE%"
            exit 1
          fi
```

### Pre-push Hook:
```bash
#!/bin/bash
# .git/hooks/pre-push

python3 run_all_tests.py --quick || {
    echo "Tests failed! Push aborted."
    exit 1
}
```

---

## 📈 Tracking Progress

Автоматически обновляется при каждом коммите:

**.ai/TEST_COVERAGE.json:**
```json
{
  "last_updated": "2025-10-09T02:30:00",
  "coverage": {
    "total": 727,
    "tested": 8,
    "percentage": 1.1
  },
  "by_priority": {
    "5": {"total": 45, "tested": 0},
    "4": {"total": 153, "tested": 0},
    "3": {"total": 505, "tested": 8}
  }
}
```

---

**Тестирование - это не опция, это часть разработки по умолчанию! 🧪**

