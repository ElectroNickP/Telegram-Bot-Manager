# 🧩 Модульная Архитектура - Feature Isolation

**Цель:** Легко добавлять фичи, изолировать баги, тестировать отдельно

---

## 🎯 ПРОБЛЕМА

Сейчас:
- `src/telegram_bot.py` - 1000+ строк, много фич вместе
- `src/app.py` - монолит Flask app
- Фичи смешаны, баг в одной ломает другую

Нужно:
- ✅ Каждая фича - отдельный модуль
- ✅ Баг изолирован в модуле
- ✅ Легко добавить/удалить фичу
- ✅ Тесты независимы

---

## 🏗️ НОВАЯ СТРУКТУРА

```
src/features/          # Все фичи изолированы
├── __init__.py
│
├── user_sessions/     # Feature: P2P Sessions
│   ├── __init__.py
│   ├── handlers.py    # Telegram handlers
│   ├── routes.py      # API endpoints
│   ├── service.py     # Business logic
│   └── tests/
│       ├── test_handlers.py
│       └── test_service.py
│
├── bot_management/    # Feature: Bot CRUD
│   ├── __init__.py
│   ├── routes.py      # API for bots
│   ├── service.py
│   └── tests/
│
├── voice_messages/    # Feature: Voice transcription
│   ├── __init__.py
│   ├── handlers.py
│   ├── service.py
│   └── tests/
│
├── link_transformation/  # Feature: URL → Buttons
│   ├── __init__.py
│   ├── handlers.py
│   ├── routes.py
│   ├── service.py
│   └── tests/
│
└── admin_panel/       # Feature: Admin controls
    ├── __init__.py
    ├── routes.py
    └── tests/

core/features/         # Core feature modules
├── __init__.py
├── base.py           # Base feature interface
└── registry.py       # Feature registry
```

---

## 📋 BASE FEATURE INTERFACE

```python
# core/features/base.py

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class FeatureMetadata:
    """Метаданные фичи"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    enabled: bool = True
    critical: bool = False  # Если True - ошибка блокирует app

class Feature(ABC):
    """
    Базовый интерфейс для всех фич
    
    Каждая фича:
    - Изолирована
    - Имеет свой lifecycle
    - Может быть включена/выключена
    - Регистрирует свои handlers/routes
    """
    
    @abstractmethod
    def metadata(self) -> FeatureMetadata:
        """Метаданные фичи"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Инициализация фичи
        
        Returns:
            True если успешно, False если ошибка
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Graceful shutdown фичи"""
        pass
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """Регистрирует Telegram handlers (опционально)"""
        pass
    
    def register_api_routes(self, app) -> None:
        """Регистрирует API endpoints (опционально)"""
        pass
    
    async def health_check(self) -> Dict:
        """
        Health check фичи
        
        Returns:
            {"status": "healthy|degraded|unhealthy", "details": {...}}
        """
        return {"status": "healthy"}
```

---

## 🔌 FEATURE REGISTRY

```python
# core/features/registry.py

from typing import Dict, List, Type
import logging

logger = logging.getLogger(__name__)

class FeatureRegistry:
    """
    Реестр всех фич
    
    - Регистрирует фичи
    - Управляет lifecycle
    - Изолирует ошибки
    """
    
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self.enabled_features: set = set()
    
    def register(self, feature: Feature) -> None:
        """Регистрирует фичу"""
        meta = feature.metadata()
        self.features[meta.name] = feature
        
        if meta.enabled:
            self.enabled_features.add(meta.name)
        
        logger.info(f"✅ Registered feature: {meta.name} v{meta.version}")
    
    async def initialize_all(self) -> Dict[str, bool]:
        """
        Инициализирует все включенные фичи
        
        Returns:
            {feature_name: success}
        """
        results = {}
        
        for name in self.enabled_features:
            feature = self.features[name]
            meta = feature.metadata()
            
            try:
                success = await feature.initialize()
                results[name] = success
                
                if success:
                    logger.info(f"✅ {name} initialized")
                else:
                    logger.warning(f"⚠️  {name} failed to initialize")
                    
                    # Если критичная фича упала - ошибка
                    if meta.critical:
                        raise RuntimeError(f"Critical feature {name} failed")
                    
            except Exception as e:
                logger.error(f"❌ {name} error: {e}")
                results[name] = False
                
                if meta.critical:
                    raise
        
        return results
    
    async def shutdown_all(self) -> None:
        """Graceful shutdown всех фич"""
        for name in self.enabled_features:
            feature = self.features[name]
            try:
                await feature.shutdown()
                logger.info(f"✅ {name} shutdown")
            except Exception as e:
                logger.error(f"❌ {name} shutdown error: {e}")
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """Регистрирует handlers всех фич"""
        for name in self.enabled_features:
            feature = self.features[name]
            try:
                feature.register_telegram_handlers(dp, bot)
                logger.info(f"✅ {name} handlers registered")
            except Exception as e:
                logger.error(f"❌ {name} handler registration error: {e}")
    
    def register_api_routes(self, app) -> None:
        """Регистрирует API routes всех фич"""
        for name in self.enabled_features:
            feature = self.features[name]
            try:
                feature.register_api_routes(app)
                logger.info(f"✅ {name} routes registered")
            except Exception as e:
                logger.error(f"❌ {name} route registration error: {e}")
    
    async def health_check_all(self) -> Dict:
        """Health check всех фич"""
        health = {}
        
        for name in self.enabled_features:
            feature = self.features[name]
            try:
                health[name] = await feature.health_check()
            except Exception as e:
                health[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health

# Global registry
feature_registry = FeatureRegistry()
```

---

## 📦 ПРИМЕР: User Sessions Feature

```python
# src/features/user_sessions/__init__.py

from core.features.base import Feature, FeatureMetadata
from core.services.user_session_service import UserSessionService
from aiogram import types
from aiogram.filters import Command

class UserSessionsFeature(Feature):
    """P2P User Sessions Feature"""
    
    def __init__(self):
        self.service = None
    
    def metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            name="user_sessions",
            version="1.0.0",
            description="P2P sessions between users",
            dependencies=["telegram_bot"],
            enabled=True,
            critical=False  # Не критична - может упасть без поломки всего
        )
    
    async def initialize(self) -> bool:
        """Initialize session service"""
        try:
            from adapters.storage.json_adapter import JsonConfigStorageAdapter
            from core.usecases.user_session_management import UserSessionManagementUseCase
            
            storage = JsonConfigStorageAdapter()
            use_case = UserSessionManagementUseCase(storage)
            self.service = UserSessionService(use_case)
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize user_sessions: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Cleanup"""
        if self.service:
            # Cleanup connections, etc
            pass
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """Register /connect, /exit handlers"""
        
        @dp.message(Command("connect"))
        async def cmd_connect(message: types.Message):
            """Handle /connect command"""
            try:
                # Изолированная логика - баг здесь не сломает другие фичи
                result = await self.service.handle_connect_command(
                    bot_id=message.bot.id,
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                )
                await message.reply(result)
                
            except Exception as e:
                logger.error(f"Connect error: {e}")
                await message.reply("❌ Ошибка подключения")
        
        @dp.message(Command("exit"))
        async def cmd_exit(message: types.Message):
            """Handle /exit command"""
            try:
                result = await self.service.handle_exit_command(
                    bot_id=message.bot.id,
                    user_id=message.from_user.id,
                )
                await message.reply(result)
                
            except Exception as e:
                logger.error(f"Exit error: {e}")
                await message.reply("❌ Ошибка выхода")
    
    def register_api_routes(self, app) -> None:
        """Register API endpoints"""
        from flask import Blueprint, jsonify, request
        
        bp = Blueprint('user_sessions', __name__, url_prefix='/api/v2/sessions')
        
        @bp.route('/active', methods=['GET'])
        def get_active_sessions():
            """Get active sessions"""
            try:
                bot_id = request.args.get('bot_id', type=int)
                sessions = self.service.get_active_sessions(bot_id)
                return jsonify(sessions)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        app.register_blueprint(bp)
    
    async def health_check(self) -> Dict:
        """Check if service is healthy"""
        if not self.service:
            return {"status": "unhealthy", "reason": "service not initialized"}
        
        try:
            # Check if can access storage
            # ping database, etc
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
```

---

## 🚀 ИСПОЛЬЗОВАНИЕ В APP

```python
# src/app.py (упрощенный)

from core.features.registry import feature_registry

# Регистрируем фичи
from src.features.user_sessions import UserSessionsFeature
from src.features.voice_messages import VoiceMessagesFeature
from src.features.link_transformation import LinkTransformationFeature

feature_registry.register(UserSessionsFeature())
feature_registry.register(VoiceMessagesFeature())
feature_registry.register(LinkTransformationFeature())

# Инициализируем
async def startup():
    results = await feature_registry.initialize_all()
    
    # Показываем что работает
    for name, success in results.items():
        if success:
            logger.info(f"✅ {name} ready")
        else:
            logger.warning(f"⚠️  {name} disabled")

# Регистрируем handlers
def setup_bot(dp, bot):
    feature_registry.register_telegram_handlers(dp, bot)

# Регистрируем API
def create_app():
    app = Flask(__name__)
    feature_registry.register_api_routes(app)
    return app

# Health check
@app.route('/health')
async def health():
    feature_health = await feature_registry.health_check_all()
    
    all_healthy = all(
        h["status"] == "healthy" 
        for h in feature_health.values()
    )
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "features": feature_health
    })
```

---

## ✅ ПРЕИМУЩЕСТВА

### 1. Изоляция багов
```python
# Баг в user_sessions НЕ ломает voice_messages
try:
    await user_sessions_feature.initialize()
except:
    logger.error("user_sessions failed, but app continues")
    # voice_messages продолжает работать!
```

### 2. Легко добавить фичу
```python
# 1. Создай src/features/new_feature/
# 2. Наследуй Feature
# 3. Зарегистрируй
feature_registry.register(NewFeature())
# Готово!
```

### 3. Легко отключить
```python
# В FeatureMetadata:
enabled=False  # Фича отключена, всё работает
```

### 4. Независимое тестирование
```python
# tests/features/test_user_sessions.py
def test_user_sessions():
    feature = UserSessionsFeature()
    await feature.initialize()
    # Тестируй изолированно!
```

### 5. Health monitoring
```bash
$ curl /health
{
  "status": "healthy",
  "features": {
    "user_sessions": {"status": "healthy"},
    "voice_messages": {"status": "degraded", "error": "OpenAI API slow"},
    "link_transformation": {"status": "healthy"}
  }
}
```

---

## 📊 МИГРАЦИЯ

### Phase 1: Create structure (30 мин)
```bash
mkdir -p src/features/{user_sessions,voice_messages,link_transformation}
mkdir -p core/features
```

### Phase 2: Implement base (1 час)
- `core/features/base.py`
- `core/features/registry.py`

### Phase 3: Migrate first feature (2 часа)
- Начни с user_sessions
- Вынеси handlers из telegram_bot.py
- Создай UserSessionsFeature

### Phase 4: Migrate остальные (4 часа)
- Voice messages
- Link transformation  
- Bot management

### Phase 5: Update app.py (1 час)
- Используй registry
- Cleanup old code

**Total:** ~8 часов, но **огромная выгода** для проекта!

---

## 🎯 РЕЗУЛЬТАТ

**До:**
```
src/telegram_bot.py (1000+ LOC)
  - user sessions
  - voice messages  
  - link transformation
  - admin commands
  - ... всё вместе
```

**После:**
```
src/features/
  ├── user_sessions/     (200 LOC, изолирован)
  ├── voice_messages/    (150 LOC, изолирован)
  ├── link_transformation/ (180 LOC, изолирован)
  └── admin_panel/       (100 LOC, изолирован)

core/features/
  ├── base.py           (100 LOC, interface)
  └── registry.py       (150 LOC, orchestration)
```

**Выгода:**
- ✅ Каждая фича ~150-200 LOC (легко понять)
- ✅ Баг изолирован
- ✅ Тесты независимы
- ✅ Новую фичу за 1 час
- ✅ Health monitoring из коробки

---

**Внедрить перед Phase 3?** Или после Phase 8?

*Рекомендую: Сейчас! Это фундамент для всех остальных фаз.*

