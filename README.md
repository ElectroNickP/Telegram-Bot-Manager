# 🚀 Telegram Bot Manager v3.8.3 - Production Ready Release

**Профессиональная система управления Telegram ботами** с веб-интерфейсом и встроенным маркетплейсом.  
✅ **Готово к развертыванию на продакшен серверах Ubuntu одной командой!**

## ⚡ Быстрый старт на Ubuntu

### 🖥️ Интерактивный режим (для разработки):
```bash
git clone https://github.com/ElectroNickP/Telegram-Bot-Manager.git
cd Telegram-Bot-Manager
git checkout prod-test
python3 start.py
```

### 🚀 Фоновый режим (для продакшена):
```bash
# Запуск в фоне (отключается от терминала)
python3 start.py --daemon

# Проверка статуса
python3 start.py --status

# Остановка
python3 start.py --stop
```

**Готово!** 🌐 Откройте http://localhost:5000  
🔐 Login: `admin` / `securepassword123`

### Что делает `start.py` автоматически:
✅ Проверяет Python 3.11+  
✅ Создает виртуальное окружение (решает externally-managed-environment)  
✅ Устанавливает зависимости  
✅ Находит свободный порт (если 5000 занят)  
✅ Запускает веб-сервер  

### 🌟 Режимы работы:

**Интерактивный режим:**
- Показывает вывод в терминале
- Останавливается при закрытии SSH
- Подходит для разработки и тестирования

**Daemon режим (`--daemon`):**
- Отключается от терминала
- Работает в фоновом режиме
- Не останавливается при отключении SSH
- Профессиональное управление через PID файлы
- Graceful shutdown при получении сигналов  

### Если Python < 3.11:
```bash
sudo apt update
sudo apt install software-properties-common  
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-venv
```

## 🌟 Особенности

- **🎯 One-Click Deploy**: Автоматическая установка на Ubuntu серверах
- **🚀 True Daemon Mode**: Настоящий Unix daemon с PID management
- **🌐 Веб-интерфейс**: Современный и интуитивно понятный UI
- **🏪 Маркетплейс**: Встроенная система для публикации и поиска ботов
- **🤖 Multi-bot поддержка**: Управление множественными ботами из одного интерфейса
- **🧠 OpenAI интеграция**: Полная поддержка GPT модели и ассистентов
- **🎤 Режим транскрибации**: Автоматическое распознавание голосовых сообщений
- **🔐 Система аутентификации**: Безопасный доступ к панели управления
- **📡 REST API**: Полнофункциональный API для интеграций
- **📁 Drag & Drop**: Удобная загрузка аватарок для ботов
- **📱 Адаптивный дизайн**: Работает на всех устройствах

## 🔧 Системные требования

- **OS**: Ubuntu 22.04+ (другие Linux дистрибутивы поддерживаются)
- **Python**: 3.11+
- **RAM**: 512MB+ 
- **Disk**: 2GB+
- **Network**: Доступ к интернету для установки зависимостей

## 📖 Документация

- [🚀 Ubuntu Quick Start](UBUNTU_QUICK_START.md) - Мгновенное развертывание
- [📋 Ubuntu Deployment Guide](UBUNTU_DEPLOYMENT_GUIDE.md) - Подробное руководство
- [🔧 Configuration Guide](QUICK_CONFIG_REFERENCE.md) - Настройка ботов
- [📈 Transcriber Mode](TRANSCRIBER_MODE_GUIDE.md) - Голосовые сообщения

## 🌐 Интерфейсы

После запуска доступно:
- **Главная**: http://localhost:5000 - Управление ботами
- **Маркетплейс**: http://localhost:5000/marketplace - Каталог ботов  
- **API v1**: http://localhost:5000/api/v1/ - REST API для интеграций
- **API v2**: http://localhost:5000/api/v2/ - Расширенный API

## 🤖 Создание бота

1. Получите токен у [@BotFather](https://t.me/BotFather)
2. Создайте ассистента в [OpenAI Platform](https://platform.openai.com/assistants)  
3. Добавьте бота через веб-интерфейс
4. Настройте параметры и запустите

## 🏪 Маркетплейс

- Публикуйте своих ботов для других пользователей
- Загружайте аватарки через drag & drop
- Добавляйте описания и теги
- Отмечайте особые боты как "featured"

## 🔐 Безопасность

- HTTP Basic Authentication 
- Валидация всех входных данных
- Защита от XSS и SQL injection
- Безопасная загрузка файлов
- Изоляция процессов ботов

## 📡 API Endpoints

### Bot Management
- `GET /api/v1/bots` - Список ботов
- `POST /api/v1/bots` - Создать бота  
- `PUT /api/v1/bots/{id}` - Обновить бота
- `DELETE /api/v1/bots/{id}` - Удалить бота

### Marketplace  
- `GET /api/v1/marketplace` - Каталог ботов
- `PUT /api/v1/marketplace/{id}` - Обновить данные маркетплейса

### File Uploads
- `POST /api/v2/upload/avatar` - Загрузка аватарок

## 🧪 Тестирование

Проект включает полный набор тестов:

```bash
python run_tests.py  # Запуск всех тестов
pytest tests/unit/   # Unit тесты  
pytest tests/integration/ # Integration тесты
pytest tests/e2e/    # End-to-end тесты
```

## 📊 Мониторинг

Система включает встроенный мониторинг:
- Логирование всех операций
- Контроль состояния ботов  
- Отслеживание производительности
- Автоматическое восстановление при сбоях

## 🔄 Обновления

Система поддерживает:
- Автоматические обновления зависимостей
- Миграции конфигураций
- Бесшовные обновления без простоя
- Резервное копирование перед обновлениями

## 🤝 Поддержка

- **Issues**: [GitHub Issues](https://github.com/ElectroNickP/Telegram-Bot-Manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ElectroNickP/Telegram-Bot-Manager/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/ElectroNickP/Telegram-Bot-Manager/wiki)

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 🏆 Версия 3.8.3 - Production Ready

### ✅ Новое в этой версии:
- **One-Click Ubuntu Deployment** - автоматическая установка на серверах
- **Virtual Environment Support** - решена проблема externally-managed-environment  
- **Improved Port Detection** - автоматический поиск свободных портов
- **Docker Testing** - тестирование в изолированной среде Ubuntu
- **Production Scripts** - оптимизированные скрипты развертывания
- **Enhanced Documentation** - подробные руководства по установке

### 🔧 Технические улучшения:
- Исправлены пути к Python executable в виртуальном окружении
- Добавлена поддержка pyproject.toml (опциональная)  
- Улучшена обработка ошибок при установке зависимостей
- Оптимизирована производительность запуска приложения
- Добавлено автоматическое создание необходимых директорий

**🚀 Проект готов к продакшену!** Развертывание занимает менее 5 минут на любом Ubuntu сервере.

---

*Создано с ❤️ для управления Telegram ботами*