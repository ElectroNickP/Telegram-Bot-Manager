# 📋 Code Meta-Information Map

**Автоматически поддерживается, не загромождает код**

---

## 🎯 КОНЦЕПЦИЯ

Вместо AI-комментариев в коде → **meta-файлы рядом с кодом**

```
core/domain/
├── user_session.py          # Чистый код
└── .meta/
    └── user_session.yaml     # Вся мета-информация
```

**Преимущества:**
- ✅ Код чистый и читаемый
- ✅ Мета-информация централизована
- ✅ Легко обновлять
- ✅ Не мешает разработчикам
- ✅ AI легко читает YAML

---

## 📄 ФОРМАТ META-ФАЙЛА

```yaml
# core/domain/.meta/user_session.yaml

file: core/domain/user_session.py
type: domain_entity
architecture_layer: domain
created: 2024-09-10
updated: 2025-10-09

context:
  - "Hexagonal Architecture - Domain Layer"
  - "Manages P2P session state between users"
  - "Pure business logic - NO external dependencies"

critical:
  - reason: "Core entity for user sessions"
  - impact: "Changes affect entire session system"
  - used_by:
    - "core/services/user_session_service.py"
    - "src/telegram_bot.py"

classes:
  SessionStatus:
    type: enum
    critical: true
    purpose: "Session lifecycle states"
    flow: "PENDING → ACTIVE → ENDED"
    warnings:
      - "Don't add statuses without updating service logic"
    
  UserInfo:
    type: value_object
    critical: true
    purpose: "Telegram user representation"
    stored_in: "bot_configs.json:online_users"
    
  UserSession:
    type: entity
    critical: true
    purpose: "P2P session between two users"
    methods:
      accept_session:
        critical: true
        changes_state: true
        status_transition: "PENDING → ACTIVE"
      end_session:
        critical: true
        changes_state: true
        status_transition: "* → ENDED"

links:
  uses:
    - "datetime"
    - "typing"
    - "dataclasses"
  used_by:
    - file: "core/services/user_session_service.py"
      methods: ["handle_connect_command", "handle_session_response"]
    - file: "src/telegram_bot.py"
      functions: ["cmd_connect", "cmd_exit"]
    - file: "adapters/storage/json_adapter.py"
      methods: ["set_user_session", "get_user_session"]

warnings:
  - "Don't change UserSession structure without data migration"
  - "Status changes must be reflected in session service"

hints:
  - "Add new session fields at the end for compatibility"
  - "Use to_dict/from_dict for serialization"
  - "Tests in tests/unit/test_user_session.py"
```

---

## 🤖 КАК AI ИСПОЛЬЗУЕТ

### 1. Быстрый поиск meta-файла:
```python
# AI ищет: core/domain/user_session.py
# Читает: core/domain/.meta/user_session.yaml
```

### 2. Получает всю информацию:
- Архитектурный слой
- Критичность
- Связи с другими файлами
- Warnings
- Hints

### 3. Код остается чистым!
```python
# Вместо:
# AI-CRITICAL: Core entity for sessions
# AI-WARNING: Don't change structure
# AI-LINK: core/services/user_session_service.py
class UserSession:
    ...

# Просто:
class UserSession:
    """P2P session between two users"""
    ...
```

---

## 📁 СТРУКТУРА META-ФАЙЛОВ

```
.meta/
├── index.yaml              # Индекс всех meta-файлов
├── core/
│   ├── domain/
│   │   ├── user_session.yaml
│   │   ├── bot.yaml
│   │   └── conversation.yaml
│   ├── services/
│   │   └── user_session_service.yaml
│   └── usecases/
│       └── user_session_management.yaml
├── src/
│   ├── app.yaml
│   ├── config_manager.yaml
│   └── api/
│       └── v2/
│           └── bots.yaml
└── adapters/
    └── storage/
        └── json_adapter.yaml
```

---

## 🔍 MASTER INDEX

```yaml
# .meta/index.yaml

version: 1.0
generated: 2025-10-09
project: Telegram Bot Manager

critical_files:
  - file: src/app.py
    meta: .meta/src/app.yaml
    reason: "Flask app entry point"
  
  - file: core/domain/user_session.py
    meta: .meta/core/domain/user_session.yaml
    reason: "Core session entity"
  
  # ... и т.д.

by_feature:
  user_sessions:
    - core/domain/.meta/user_session.yaml
    - core/services/.meta/user_session_service.yaml
    - core/usecases/.meta/user_session_management.yaml
  
  bot_management:
    - core/domain/.meta/bot.yaml
    - src/.meta/config_manager.yaml
    - src/api/v2/.meta/bots.yaml

by_layer:
  domain:
    - core/domain/.meta/user_session.yaml
    - core/domain/.meta/bot.yaml
    - core/domain/.meta/conversation.yaml
  
  use_cases:
    - core/usecases/.meta/user_session_management.yaml
    - core/usecases/.meta/bot_management.yaml

dangerous_zones:
  - file: src/config_manager.py
    meta: .meta/src/config_manager.yaml
    reason: "All bots depend on this"
  
  - file: adapters/storage/json_adapter.py
    meta: .meta/adapters/storage/json_adapter.yaml
    reason: "Data persistence layer"
```

---

## 🛠️ ГЕНЕРАТОР META-ФАЙЛОВ

```python
# .ai/tools/generate-meta.py

def generate_meta_from_code(file_path: Path) -> dict:
    """
    Анализирует код и генерирует meta-информацию
    
    - Парсит AST
    - Находит классы/функции
    - Определяет imports
    - Ищет где используется (grep)
    - Генерирует YAML
    """
    pass

def update_meta_index():
    """Обновляет master index"""
    pass
```

---

## 💡 ПРЕИМУЩЕСТВА

### Для разработчиков:
- ✅ **Код чистый** - нет лишних комментариев
- ✅ **Мета отдельно** - не мешает
- ✅ **Git diff чище** - meta изменения отдельно

### Для AI:
- ✅ **Вся информация в одном месте**
- ✅ **Структурированная** (YAML)
- ✅ **Легко парсить**
- ✅ **Быстро найти** через index

### Для проекта:
- ✅ **Масштабируется** - сотни файлов OK
- ✅ **Поддерживается** - можно авто-генерировать
- ✅ **Не захламляет** код
- ✅ **Опционально** - можно не использовать

---

## 🚀 МИГРАЦИЯ

### 1. Создать структуру:
```bash
mkdir -p .meta/{core/{domain,services,usecases},src/api/v2,adapters/storage}
```

### 2. Сгенерировать meta для критичных файлов:
```bash
python3 .ai/tools/generate-meta.py core/domain/user_session.py
python3 .ai/tools/generate-meta.py src/config_manager.py
# и т.д.
```

### 3. Создать master index:
```bash
python3 .ai/tools/build-index.py
```

---

## 📖 AI WORKFLOW

```python
# 1. AI хочет изменить user_session.py

# 2. Читает meta:
meta = read_yaml('.meta/core/domain/user_session.yaml')

# 3. Видит:
# - critical: true
# - warnings: ["Don't change structure"]
# - used_by: [session_service, telegram_bot]

# 4. Проверяет связанные файлы

# 5. Делает изменения аккуратно

# 6. Обновляет meta если структура изменилась
```

---

## ⏱️ TIME ESTIMATE

- Создать структуру: 5 мин
- Написать generate-meta.py: 2 часа
- Сгенерировать meta для 10 критичных файлов: 30 мин
- Создать master index: 30 мин
- Обновить .ai/README.md: 15 мин

**Total: ~3.5 часа**

---

## ✅ РЕЗУЛЬТАТ

```
Было:
core/domain/user_session.py (220 lines)
  - 30 lines AI comments
  - 190 lines code

Стало:
core/domain/user_session.py (190 lines) ← Чистый код!
.meta/core/domain/user_session.yaml (50 lines) ← Вся мета
```

**Код чище, информации больше!** 🎉

