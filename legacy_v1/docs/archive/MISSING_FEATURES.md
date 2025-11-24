# ❌ Потерянный функционал при рефакторинге

## 📋 Что было потеряно

### 1. 🧠 Режим "только транскрибация"
**Было:** `enable_ai_responses: false` → бот транскрибирует голос, но не отвечает через GPT  
**Сейчас:** Нет этого режима

### 2. 🎤 TTS голосовые ответы
**Было:**
- `enable_voice_responses: true/false`
- `voice_model: "tts-1"` или `"tts-1-hd"`
- `voice_type: "alloy"` (или echo, fable, onyx, nova, shimmer)

**Сейчас:** TTS вообще отсутствует

### 3. 📊 Настраиваемый контекст per-bot
**Было:** `group_context_limit: 5-50` индивидуально для каждого бота  
**Сейчас:** Фиксированные 20 для всех

### 4. 🖥️ Web UI для управления
**Было:**
- Веб-интерфейс для создания/редактирования ботов
- Чекбоксы для включения фич
- Slider для контекста
- Выбор голоса из dropdown

**Сейчас:** Только JSON конфиги

### 5. 🔗 Расширенная настройка Link Transformation
**Было:**
- Transformation rules с match patterns
- Кастомные кнопки по доменам
- process_ai_responses / process_user_messages
- Детальный UI для настройки

**Сейчас:** Базовая трансформация без rules

### 6. 🏪 Marketplace
**Было:** Интеграция с маркетплейсом ботов  
**Сейчас:** Отсутствует

### 7. 🤖 Admin Bot
**Было:** Отдельный telegram бот для администрирования  
**Сейчас:** Отсутствует

---

## ✅ Как восстановить

### Вариант 1: Улучшить существующие плагины

#### `plugins/voice_processor/config.json`
```json
{
  "enabled": true,
  "settings": {
    "transcription_only": false,
    "enable_tts_responses": true,
    "voice_model": "tts-1",
    "voice_type": "alloy",
    "available_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
  }
}
```

#### `plugins/gpt_reply/config.json`
```json
{
  "enabled": true,
  "settings": {
    "context_limit": 15,
    "min_context": 5,
    "max_context": 50
  }
}
```

#### `plugins/link_transformer/config.json`
```json
{
  "enabled": true,
  "settings": {
    "transformation_rules": [
      {
        "match_type": "domain",
        "match_value": "google.com",
        "button_text": "Open Google",
        "button_emoji": "🔍"
      }
    ]
  }
}
```

---

### Вариант 2: Создать UI plugin

Создать `plugins/web_ui/` для управления всеми настройками через веб-интерфейс.

---

### Вариант 3: Per-bot конфигурация

Изменить структуру чтобы каждый "бот" мог иметь свои настройки плагинов:

```yaml
bots:
  bot1:
    telegram_token: ${BOT1_TOKEN}
    plugins:
      voice_processor:
        enabled: true
        transcription_only: false
        voice_type: "alloy"
      gpt_reply:
        enabled: true
        context_limit: 15
      
  bot2:
    telegram_token: ${BOT2_TOKEN}
    plugins:
      voice_processor:
        enabled: true
        transcription_only: true  # Только транскрибация!
      gpt_reply:
        enabled: false  # AI ответы выключены
```

---

## 🎯 Рекомендации

### Приоритет 1 (критично):
1. ✅ TTS голосовые ответы
2. ✅ Режим "только транскрибация"
3. ✅ Настраиваемый контекст

### Приоритет 2 (важно):
4. ✅ Web UI для управления
5. ✅ Transformation rules для ссылок

### Приоритет 3 (опционально):
6. Marketplace
7. Admin Bot

---

## 📝 Следующие шаги

1. **Добавить TTS в voice_processor plugin**
2. **Добавить настройку контекста в config.yaml**
3. **Создать режим transcription_only**
4. **Портировать Web UI (опционально)**

Хочешь, чтобы я добавил этот функционал сейчас?


