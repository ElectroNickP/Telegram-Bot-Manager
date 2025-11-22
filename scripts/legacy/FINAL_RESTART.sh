#!/bin/bash

# FINAL RESTART - kills everything and starts fresh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔄 ФИНАЛЬНЫЙ ПЕРЕЗАПУСК - УБИВАЕМ ВСЁ                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Kill ALL Python processes related to our project
echo "1. Убиваю ВСЕ процессы проекта..."
pkill -9 -f "/home/nick/Projects/Phuket/Telegram-Bot-Manager.*python"
pkill -9 -f "Telegram-Bot-Manager.*app.py"
pkill -9 -f "Telegram-Bot-Manager.*start.py"
sleep 5

# 2. Clear cache
echo "2. Очищаю кэш..."
cd /home/nick/Projects/Phuket/Telegram-Bot-Manager
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 3. Reset Telegram webhook
echo "3. Сбрасываю Telegram webhook..."
BOT_TOKEN="7684104886:AAHC_yil3ChAqO1ffXCHdEdXiw96jHszm6Y"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" > /dev/null
sleep 3

# 4. Wait for everything to die
echo "4. Жду полной остановки..."
sleep 5

# 5. Start fresh
echo "5. Запускаю приложение..."
python3 start.py > /tmp/final_start.log 2>&1 &
sleep 15

# 6. Start bot
echo "6. Запускаю бота..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start | jq -r '.message'
sleep 5

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ПЕРЕЗАПУСК ЗАВЕРШЁН                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check status
echo "Проверяю статус:"
echo ""
echo "1. Процессы:"
ps aux | grep "python.*app.py" | grep -v grep | awk '{print "   PID:", $2}'
echo ""
echo "2. Последний polling:"
tail -20 ./src/bot.log | grep "Run polling" | tail -1
echo ""
echo "3. API Telegram:"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates" | jq -r 'if .ok then "   ✅ OK - нет конфликтов" else "   ❌ ERROR: \(.description)" end'
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  📱 ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot СЕЙЧАС!                 ║"
echo "╚════════════════════════════════════════════════════════════╝"



