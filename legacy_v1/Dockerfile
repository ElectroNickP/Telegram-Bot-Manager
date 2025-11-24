# Используем официальный slim образ для уменьшения размера и повышения безопасности
FROM python:3.11-slim as builder

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Устанавливаем системные зависимости для сборки (если нужны, например gcc)
# Для python-slim часто нужны build-essential для сборки некоторых колес
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt requirements-prod.txt ./

# Создаем venv и устанавливаем зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Устанавливаем зависимости (сначала prod, потом обычные)
RUN pip install -r requirements-prod.txt && \
    pip install -r requirements.txt && \
    pip install gunicorn

# -------------------------------------------------------------------
# Финальный этап (Runtime)
# -------------------------------------------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py

WORKDIR /app

# Создаем непривилегированного пользователя
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app/logs /app/static/uploads && \
    chown -R appuser:appuser /app

# Копируем venv из builder
COPY --from=builder /opt/venv /opt/venv

# Копируем код приложения
# Важно: копируем только src в корень рабочей директории или сохраняем структуру
# Так как приложение ожидает запуск внутри src (из-за импортов), скопируем содержимое src в /app
# ИЛИ скопируем src в /app/src и настроим PYTHONPATH. 
# Лучший вариант: соблюдать структуру репозитория.
COPY src /app/src
COPY plugins /app/plugins
COPY bot_configs.json /app/src/bot_configs.json
# (Опционально) Если есть другие нужные файлы в корне

# Настраиваем права
RUN chown -R appuser:appuser /app

# Переключаемся на пользователя
USER appuser

# Рабочая директория - src, так как imports в коде часто relative или рассчитывают на корень в src
WORKDIR /app/src

# Открываем порт
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/system/health || exit 1

# Запуск через Gunicorn
# Используем конфиг gunicorn_config.py, который лежит в src/
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:create_app()"]

