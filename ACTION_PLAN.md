# 🚀 ACTION PLAN - Немедленные действия для масштабирования

**Приоритет:** CRITICAL → HIGH → MEDIUM → LOW  
**Оценка времени:** Реалистичная для одного разработчика с AI

---

## 🚨 CRITICAL (Сделать СЕЙЧАС - 1-3 дня)

### 1. ❌ FIX: Security - Hardcoded Credentials

**Проблема:** Пароли в коде - критичная уязвимость

**Файлы:**
- `src/shared/auth.py` (предположительно)
- Возможно в `src/config_manager.py`

**Действия:**
```bash
# 1. Создать .env.example
cat > .env.example << 'EOF'
# Telegram Bot Manager Configuration

# Admin Credentials (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

# OpenAI API
OPENAI_API_KEY=sk-...

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...

# Flask
SECRET_KEY=your-secret-key-here
SESSION_TYPE=filesystem

# Generate password hash:
# python3 -c "import hashlib; print(hashlib.sha256(b'your-password').hexdigest())"
EOF

# 2. Создать .env (не коммитить!)
cp .env.example .env
nano .env  # Заполнить реальными значениями

# 3. Обновить код для чтения из env
```

**Код изменения:**
```python
# src/shared/auth.py
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials against environment variables."""
    if username != ADMIN_USERNAME:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == ADMIN_PASSWORD_HASH
```

**Проверка:**
```bash
# Test login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-new-password"}'
```

**Время:** 2-3 часа

---

### 2. ❌ CLEANUP: Remove Log Files from Git

**Проблема:** Log files в репозитории (info disclosure)

**Действия:**
```bash
# 1. Обновить .gitignore
cat >> .gitignore << 'EOF'

# Logs (comprehensive)
*.log
logs/
**/logs/
**/*.log
test_*.log
src/bot.log
src/logs/
test-results/

# Environment
.env
.env.local
.env.*.local

# Backups
backups/*.json
!backups/.gitkeep

# Temporary files
*.tmp
*.temp
.DS_Store
EOF

# 2. Удалить tracked logs
git rm --cached logs/*.log
git rm --cached src/bot.log
git rm --cached test_start.log
git rm --cached test-results/*.log
git rm --cached tests/test.log

# 3. Создать .gitkeep для пустых папок
touch logs/.gitkeep
touch backups/.gitkeep
touch test-results/.gitkeep

# 4. Коммит
git add .gitignore */*/gitkeep
git commit -m "chore: Remove log files from git, update .gitignore"
```

**Время:** 30 минут

---

### 3. ⚠️ UPDATE: Sync Requirements

**Проблема:** Несоответствие версий в requirements.txt и pyproject.toml

**Действия:**
```bash
# 1. Проверить текущие версии
pip list | grep -E "flask|openai|aiogram"

# 2. Обновить requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies (Production)
openai>=1.0.0,<2.0.0
aiogram>=3.0.0,<4.0.0
python-dotenv>=1.0.0
pydub>=0.25.0

# Web framework
flask>=3.0.0
flask_httpauth>=4.8.0
flask-restx>=1.3.0
flask-limiter>=3.5.0  # NEW: Rate limiting
marshmallow>=3.20.0

# System utilities
psutil>=5.9.0
Pillow>=10.0.0

# API & Validation
jsonschema>=4.0.0
PyYAML>=6.0.0
requests>=2.31.0

# Security (NEW)
python-jose[cryptography]>=3.3.0  # JWT
passlib[bcrypt]>=1.7.4            # Password hashing

# Development and testing
pytest>=7.4.0
pytest-asyncio>=0.21.0  
pytest-cov>=4.1.0
pytest-html>=4.1.0
pytest-mock>=3.11.0
selenium>=4.15.0
locust>=2.17.0
EOF

# 3. Sync pyproject.toml dependencies

# 4. Install
pip install -r requirements.txt
```

**Время:** 1 час

---

## ⚡ HIGH PRIORITY (1-2 недели)

### 4. 📝 CREATE: AI Context Files

**Цель:** Упростить работу AI-ассистенту

**Файлы уже созданы:**
- ✅ `CONTEXT.md` - Главный контекст
- ✅ `MODULE_MAP.md` - Карта модулей
- ✅ `PROJECT_AUDIT_COMPREHENSIVE.md` - Полный аудит

**Создать дополнительно:**

```bash
# 1. Dependency Graph
cat > docs/DEPENDENCY_GRAPH.md << 'EOF'
# Dependency Graph

## High-Level
Apps → Entrypoints → Use Cases → Domain
                ↓
           Adapters

## Detailed
[Mermaid diagram here]
EOF

# 2. Troubleshooting Guide
cat > docs/TROUBLESHOOTING.md << 'EOF'
# Troubleshooting Guide

## Bot not starting
- Check token validity
- Check OpenAI API key
- Check port availability

## Session not working
- Ensure bot_id in config
- Check storage permissions
- Verify user activity tracking
EOF

# 3. Contributing Guide
cat > CONTRIBUTING.md << 'EOF'
# Contributing Guidelines

## Code Style
- Black for formatting
- Ruff for linting
- Type hints required

## Testing
- Write tests first (TDD)
- Minimum 70% coverage
- All tests must pass
EOF
```

**Время:** 1 неделя (по мере работы)

---

### 5. 🔒 ADD: Rate Limiting

**Цель:** Защита от DoS

**Код:**
```python
# requirements.txt
flask-limiter>=3.5.0

# src/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Redis для production
)

# Apply to routes
@app.route("/api/v2/bots", methods=["POST"])
@limiter.limit("10 per minute")
@api_v2_auth_required
def create_bot_v2():
    ...
```

**Время:** 4 часа

---

### 6. 📊 ADD: OpenAPI Documentation

**Цель:** Интерактивная API документация

**Код:**
```python
# requirements.txt
flasgger>=0.9.7

# src/app.py
from flasgger import Swagger

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger = Swagger(app, config=swagger_config)

# В каждом endpoint добавить docstring
@app.route("/api/v2/bots", methods=["POST"])
def create_bot_v2():
    """
    Create new bot
    ---
    tags:
      - bots
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
            - token
          properties:
            name:
              type: string
            token:
              type: string
    responses:
      201:
        description: Bot created successfully
    """
    ...
```

**Проверка:**
http://localhost:5000/api/docs

**Время:** 1 неделя (документировать все endpoints)

---

### 7. 🧪 INCREASE: Test Coverage

**Цель:** Довести до 70%+

**Приоритетные модули:**
```
core/domain/          40% → 80%
core/usecases/        60% → 80%
core/services/        30% → 70%
adapters/             50% → 70%
```

**План:**
```bash
# 1. Проверить текущее покрытие
pytest --cov=core --cov=adapters --cov=apps --cov-report=html

# 2. Открыть htmlcov/index.html
# 3. Найти uncovered lines
# 4. Написать тесты для:
#    - Happy path
#    - Edge cases
#    - Error handling

# Focus areas:
# - core/domain/user_session.py (methods)
# - core/usecases/bot_management.py (error cases)
# - adapters/storage/json_adapter.py (concurrent access)
# - src/telegram_bot.py (handlers)
```

**Время:** 2 недели

---

## 📈 MEDIUM PRIORITY (2-4 недели)

### 8. 🔄 REFACTOR: Unified Configuration

**Цель:** Centralized config management

**Создать:**
```python
# core/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Admin
    admin_username: str = "admin"
    admin_password_hash: str
    
    # Flask
    secret_key: str
    session_type: str = "filesystem"
    
    # OpenAI
    openai_api_key: str
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    
    # Database
    database_url: str = "json://bot_configs.json"
    
    # Server
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    
    # Features
    link_transformation_enabled: bool = True
    sessions_enabled: bool = True
    voice_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Usage
settings = Settings()
```

**Время:** 1 неделя

---

### 9. 🗄️ ADD: Database Storage Adapter

**Цель:** Scalable storage вместо JSON

**Создать:**
```python
# adapters/storage/postgresql_adapter.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.ports.storage import ConfigStoragePort

class PostgreSQLStorageAdapter(ConfigStoragePort):
    """PostgreSQL implementation of ConfigStoragePort."""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def read_config(self) -> Dict[str, Any]:
        with self.Session() as session:
            # Implementation
            ...
```

**Migration:**
```python
# infra/scripts/migrate_json_to_db.py
def migrate():
    # Read from JSON
    json_adapter = JsonConfigStorageAdapter()
    data = json_adapter.read_config()
    
    # Write to DB
    db_adapter = PostgreSQLStorageAdapter(settings.database_url)
    db_adapter.write_config(data)
```

**Время:** 2 недели

---

### 10. 📊 ADD: Monitoring & Metrics

**Цель:** Observability

**Добавить:**
```python
# requirements.txt
prometheus-client>=0.19.0
python-json-logger>=2.0.7

# infra/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Metrics
bot_messages_total = Counter('bot_messages_total', 'Total messages processed', ['bot_id', 'type'])
bot_response_time = Histogram('bot_response_time_seconds', 'Response time')
active_sessions = Gauge('active_sessions_total', 'Active user sessions')

# Usage in code
@bot_response_time.time()
async def process_message(message):
    bot_messages_total.labels(bot_id=1, type='text').inc()
    ...

# Endpoint
@app.route("/metrics")
def metrics():
    return generate_latest()
```

**Dashboard:**
- Prometheus + Grafana
- Или простой `/metrics` endpoint

**Время:** 1 неделя

---

## 🌟 LOW PRIORITY (1-3 месяца)

### 11. 🚀 IMPLEMENT: Caching Layer

**Redis для:**
- Session state
- User activity
- Bot configurations (hot data)
- Rate limiting counters

**Время:** 1 неделя

---

### 12. 📦 CREATE: Docker Compose for Development

**Цель:** Reproducible dev environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/botmanager
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: botmanager
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:7-alpine
```

**Время:** 3 дня

---

### 13. 🔧 CREATE: Admin CLI Tools

**Цель:** Management commands

```python
# infra/scripts/cli.py
import click

@click.group()
def cli():
    """Telegram Bot Manager CLI"""
    pass

@cli.command()
def cleanup_sessions():
    """Cleanup old sessions"""
    ...

@cli.command()
@click.option('--bot-id', required=True)
def restart_bot(bot_id):
    """Restart specific bot"""
    ...

if __name__ == '__main__':
    cli()
```

**Время:** 1 неделя

---

### 14. 📱 IMPROVE: Web UI/UX

**Focus:**
- Real-time updates (WebSockets)
- Better mobile experience
- Dark mode
- Interactive dashboard

**Время:** 2-3 недели

---

## 📅 TIMELINE

```
Week 1-2:  CRITICAL items (1-3)
Week 3-4:  HIGH priority (4-7)
Week 5-8:  MEDIUM priority (8-10)
Week 9+:   LOW priority (11-14)
```

## ✅ DEFINITION OF DONE

Каждая задача считается выполненной когда:
- [ ] Код написан и прошел review
- [ ] Тесты написаны и проходят
- [ ] Documentation обновлена
- [ ] Changelog обновлен
- [ ] PR merged в develop

---

**Создан:** AI Assistant  
**Дата:** 15 октября 2025  
**Версия:** 1.0

