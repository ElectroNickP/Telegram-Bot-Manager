#!/bin/bash

# Clean restart script - kills ALL old bot instances

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔄 ПОЛНАЯ ОЧИСТКА И ПЕРЕЗАПУСК                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Kill all app.py and start.py processes
echo "1. Останавливаю все процессы..."
pkill -9 -f "python.*app.py" 2>/dev/null
pkill -9 -f "start.py" 2>/dev/null
pkill -9 -f "tail.*bot.log" 2>/dev/null
sleep 3

# 2. Clear Python cache
echo "2. Очищаю Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 3. Delete webhook and drop pending updates
echo "3. Сбрасываю webhook и pending updates..."
BOT_TOKEN="7684104886:AAHC_yil3ChAqO1ffXCHdEdXiw96jHszm6Y"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" > /dev/null

# 4. Wait for old processes to die
echo "4. Жду завершения старых процессов..."
sleep 5

# 5. Start fresh
echo "5. Запускаю бота заново..."
python3 start.py > /tmp/bot_clean_start.log 2>&1 &
sleep 12

# 6. Start bot via API
echo "6. Активирую бота через API..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start | jq -r '.message'
sleep 3

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ БОТ ПЕРЕЗАПУЩЕН                                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Проверяю статус:"
tail -20 ./src/bot.log | grep -E "Run polling|ERROR"
echo ""
echo "📱 ТЕПЕРЬ ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot!"



