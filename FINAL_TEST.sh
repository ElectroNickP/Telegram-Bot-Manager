#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎯 ФИНАЛЬНЫЙ ТЕСТ - ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Статус:"
echo "  ✅ Процессов app.py: $(ps aux | grep 'python.*app.py' | grep -v grep | wc -l)"
echo "  ✅ Polling активен: $(tail -5 ./src/bot.log | grep -q 'Run polling' && echo 'ДА' || echo 'НЕТ')"
echo ""
echo "📱 ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot ПРЯМО СЕЙЧАС!"
echo ""
echo "Мониторю 30 секунд..."
echo ""

for i in {1..30}; do
    sleep 1
    
    # Проверяем обработку
    if tail -10 ./src/bot.log | grep -q "✅ Processing message: PRIVATE CHAT"; then
        echo ""
        echo "🎉🎉🎉 СООБЩЕНИЕ ПОЛУЧЕНО И ОБРАБАТЫВАЕТСЯ! 🎉🎉🎉"
        echo ""
        tail -15 ./src/bot.log | grep -E "(✅ Processing|Update id=)" | tail -5
        echo ""
        echo "✅ БОТ РАБОТАЕТ!"
        exit 0
    fi
    
    # Проверяем updates
    if tail -10 ./src/bot.log | grep -q "Update id="; then
        LAST_UPDATE=$(tail -10 ./src/bot.log | grep "Update id=" | tail -1)
        echo "📨 Update: $LAST_UPDATE"
    fi
    
    # Проверяем ошибки
    if tail -5 ./src/bot.log | grep -iq "conflict"; then
        echo ""
        echo "❌ КОНФЛИКТ ОБНАРУЖЕН!"
        tail -5 ./src/bot.log | grep -i conflict
        echo ""
        echo "Есть другой процесс который делает getUpdates!"
        ps aux | grep python | grep -v grep | grep -v "venv/lib"
        exit 1
    fi
    
    if [ $((i % 10)) -eq 0 ]; then
        echo "⏳ $i секунд..."
    fi
done

echo ""
echo "⏰ 30 секунд прошло - сообщений не получено"
echo ""
echo "Последние логи:"
tail -15 ./src/bot.log



