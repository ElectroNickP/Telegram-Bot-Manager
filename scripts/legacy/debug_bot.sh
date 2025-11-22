#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🔍 BOT DEBUG TOOL - REAL-TIME MONITORING        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Check bot status in config
echo -e "${YELLOW}📋 1. BOT STATUS IN CONFIG:${NC}"
cat bot_configs.json | jq '.bots."1".status' 2>/dev/null || echo "Error reading config"
echo ""

# 2. Check running processes
echo -e "${YELLOW}🔄 2. RUNNING BOT PROCESSES:${NC}"
ps aux | grep -E "python.*(app\.py|telegram_bot|bot\.main)" | grep -v grep
echo ""

# 3. Check if bot is polling
echo -e "${YELLOW}📡 3. CHECKING TELEGRAM POLLING:${NC}"
tail -5 ./src/bot.log | grep -E "(polling|Start polling|Run polling)" || echo "No polling logs found"
echo ""

# 4. Check recent updates
echo -e "${YELLOW}📨 4. RECENT TELEGRAM UPDATES (last 10):${NC}"
tail -20 ./src/bot.log | grep -E "Update id=" || echo "No updates received"
echo ""

# 5. Check for errors
echo -e "${YELLOW}❌ 5. RECENT ERRORS:${NC}"
tail -50 ./src/bot.log | grep -iE "(error|exception|conflict|failed)" || echo "No errors found"
echo ""

# 6. Live monitoring
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎯 LIVE MONITORING - Send message to bot NOW!            ║${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop                                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

tail -f ./src/bot.log | while read line; do
    if echo "$line" | grep -q "✅ Processing message: PRIVATE CHAT"; then
        echo -e "${GREEN}🎉 PRIVATE MESSAGE: $line${NC}"
    elif echo "$line" | grep -q "✅ Processing message"; then
        echo -e "${GREEN}✅ GROUP MESSAGE: $line${NC}"
    elif echo "$line" | grep -q "Update id="; then
        # Extract duration
        DURATION=$(echo "$line" | grep -oP "Duration \K[0-9]+")
        if [ "$DURATION" = "0" ]; then
            echo -e "${YELLOW}⏭️ IGNORED: $line${NC}"
        else
            echo -e "${GREEN}✅ PROCESSED: $line${NC}"
        fi
    elif echo "$line" | grep -iq "error"; then
        echo -e "${RED}❌ ERROR: $line${NC}"
    elif echo "$line" | grep -q "⏭️ Игнорирую"; then
        echo -e "${YELLOW}⏭️ IGNORED: $line${NC}"
    elif echo "$line" | grep -q "Получено"; then
        echo -e "${BLUE}📨 RECEIVED: $line${NC}"
    elif echo "$line" | grep -q "Run polling"; then
        echo -e "${GREEN}🚀 POLLING STARTED: $line${NC}"
    else
        echo "$line"
    fi
done

