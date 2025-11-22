# 🧪 Bot Debugging - Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# Terminal 1: Start bot
sudo pkill -9 -f 'bot.main'  # Kill conflicts
./start_bot_safe.sh           # Start bot safely

# Terminal 2: Monitor logs
./debug_bot.sh                # Live monitoring

# Telegram App: Send message to @diosybot
```

---

## 📚 Available Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `start_bot_safe.sh` | Safe bot startup | `./start_bot_safe.sh` |
| `debug_bot.sh` | Live log monitoring | `./debug_bot.sh` |
| `kill_conflicts.sh` | Find conflicts | `./kill_conflicts.sh` |
| `test_bot_real.py` | Testing guide | `python3 test_bot_real.py` |
| `webhook_tester.py` | Webhook info | `python3 webhook_tester.py` |

---

## 📖 Full Documentation

**[PROFESSIONAL_DEBUGGING_GUIDE.md](./PROFESSIONAL_DEBUGGING_GUIDE.md)** - Complete guide with 5 testing methods

---

## 🔧 Common Issues

### Bot not responding?
```bash
# Check for conflicts
ps aux | grep "bot.main"

# Kill conflicts
sudo pkill -9 -f 'bot.main'

# Restart
./start_bot_safe.sh
```

### Logs not showing?
```bash
# Clear Python cache
find . -name "*.pyc" -delete

# Restart bot
curl -X POST http://127.0.0.1:5000/api/bots/1/stop -u admin:admin
curl -X POST http://127.0.0.1:5000/api/bots/1/start -u admin:admin
```

---

## 🎯 What to Look For

**✅ Good logs:**
```
🎉 PRIVATE MESSAGE: ✅ Processing message: PRIVATE CHAT from user 123456
✅ PROCESSED: Update id=746765432 is handled. Duration 720 ms
```

**⏭️ Ignored messages:**
```
⏭️ IGNORED: Update id=746765433 is handled. Duration 0 ms
```

**❌ Errors:**
```
❌ ERROR: TelegramConflictError: Conflict: terminated by other getUpdates
```

---

## 💡 Pro Tips

1. **Always use 2 terminals** - one for bot, one for monitoring
2. **Check for conflicts first** - `ps aux | grep "bot.main"`
3. **Clear cache after code changes** - `find . -name "*.pyc" -delete`
4. **Use structured logging** - see logs in real-time with `debug_bot.sh`
5. **Test with real messages** - from Telegram app, not API

---

## 📞 Need Help?

Read: **[PROFESSIONAL_DEBUGGING_GUIDE.md](./PROFESSIONAL_DEBUGGING_GUIDE.md)**

It covers:
- 5 professional testing methods
- Webhook testing with ngrok
- Unit tests with mocks
- Integration tests
- Production monitoring
- Best practices




