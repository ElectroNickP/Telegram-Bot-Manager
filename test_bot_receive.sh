#!/bin/bash

BOT_TOKEN="7684104886:AAHC_yil3ChAqO1ffXCHdEdXiw96jHszm6Y"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧪 ТЕСТ ПОЛУЧЕНИЯ СООБЩЕНИЙ                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot ПРЯМО СЕЙЧАС!"
echo ""
echo "Мониторю 30 секунд..."
echo ""

START_TIME=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt 30 ]; then
        echo ""
        echo "⏰ 30 секунд прошло"
        break
    fi
    
    # Проверяем Telegram API
    UPDATES=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?limit=1&timeout=1")
    UPDATE_COUNT=$(echo "$UPDATES" | jq -r '.result | length')
    
    if [ "$UPDATE_COUNT" != "0" ]; then
        echo ""
        echo "🎉 СООБЩЕНИЕ ПОЛУЧЕНО ОТ TELEGRAM API!"
        echo ""
        echo "$UPDATES" | jq -r '.result[] | "Update \(.update_id): \(.message.text // "no text")"'
        echo ""
        echo "✅ Telegram API работает и отдаёт updates!"
        echo ""
        echo "Проверяю получил ли наш бот:"
        sleep 2
        if tail -10 ./src/bot.log | grep -q "Update id="; then
            echo "✅ НАШ БОТ ТОЖЕ ПОЛУЧИЛ!"
            tail -15 ./src/bot.log | grep -E "(Update id=|✅ Processing)" | tail -5
        else
            echo "❌ НАШ БОТ НЕ ПОЛУЧИЛ!"
            echo ""
            echo "Проблема: Наш бот не обрабатывает updates"
            echo "Последние логи:"
            tail -10 ./src/bot.log
        fi
        exit 0
    fi
    
    # Проверяем логи нашего бота
    if tail -5 ./src/bot.log 2>/dev/null | grep -q "Update id="; then
        echo ""
        echo "✅ НАШ БОТ ПОЛУЧИЛ UPDATE!"
        tail -15 ./src/bot.log | grep -E "(Update id=|✅ Processing)" | tail -5
        exit 0
    fi
    
    if [ $((ELAPSED % 5)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        echo "⏳ $ELAPSED секунд... (отправьте сообщение если ещё не отправили)"
    fi
    
    sleep 1
done

echo ""
echo "❌ СООБЩЕНИЙ НЕ ПОЛУЧЕНО"
echo ""
echo "Возможные причины:"
echo "1. Вы не отправили сообщение"
echo "2. Бот не запущен"
echo "3. Есть конфликтующий процесс"
echo ""
echo "Проверка:"
ps aux | grep "bot.main" | grep -v grep && echo "❌ КОНФЛИКТ НАЙДЕН!" || echo "✅ Конфликтов нет"



