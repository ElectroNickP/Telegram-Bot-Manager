#!/bin/bash

# Kill conflicting bot processes
echo "🛑 Убиваю конфликтующие процессы..."

# Find and kill bot.main processes
PIDS=$(ps aux | grep "python.*bot\.main" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ Конфликтующих процессов не найдено"
    exit 0
fi

echo "Найдены процессы: $PIDS"
echo "Выполните команду:"
echo ""
echo "sudo kill -9 $PIDS"
echo ""
echo "Или:"
echo "sudo pkill -9 -f 'bot.main'"




