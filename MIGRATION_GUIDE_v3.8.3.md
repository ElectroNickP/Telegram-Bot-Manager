# 🔄 Migration Guide to v3.8.3

**Date:** 2025-10-25  
**From:** Any version < 3.8.3  
**To:** v3.8.3 - Production Ready Release

---

## 📋 Overview

Version 3.8.3 introduces significant security enhancements:
- **HTTPS enforcement** for production deployments
- **JWT authentication** for API v2
- **Encryption at rest** for sensitive data (tokens, API keys)

This guide helps you migrate safely.

---

## 🚨 Breaking Changes

### 1. Environment Variables Required

Several features now require environment variables for security:

| Variable | Required | Purpose | How to Generate |
|----------|----------|---------|-----------------|
| `FLASK_SECRET_KEY` | **Yes** | Session encryption | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `JWT_SECRET_KEY` | Recommended | JWT tokens | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | Recommended | Encrypt secrets at rest | See below |

### 2. Automatic Secret Encryption

**HIGH-03 Feature:** Bot configurations with sensitive data (telegram tokens, API keys) are now encrypted automatically.

**What happens:**
- First save after upgrade → Creates backup → Encrypts secrets
- Backups stored as: `bot_configs.json.backup_YYYYMMDD_HHMMSS`
- Without `ENCRYPTION_KEY`: Secrets stored in plaintext (warning logged)

### 3. HTTPS Enforcement

**HIGH-01 Feature:** Production deployments now enforce HTTPS.

**Control:**
- Set `ENVIRONMENT=production` → Automatic HTTPS enforcement
- Or set `FORCE_HTTPS=true` manually
- Includes HSTS headers (1 year max-age)

---

## 🔧 Step-by-Step Migration

### Step 1: Backup Current Configuration

```bash
# Backup your current configuration
cd /home/nick/Projects/Phuket/Telegram-Bot-Manager
cp bot_configs.json bot_configs.json.pre-3.8.3-backup
cp -r src/bot_configs.json src/bot_configs.json.pre-3.8.3-backup 2>/dev/null || true
```

### Step 2: Generate Security Keys

```bash
# Create .env file from template
cp .env.example .env

# Generate all secrets at once
python3 << 'EOF'
import secrets
from cryptography.fernet import Fernet

print("\n🔐 Generated Security Keys for v3.8.3:\n")
print("FLASK_SECRET_KEY=" + secrets.token_hex(32))
print("JWT_SECRET_KEY=" + secrets.token_hex(32))
print("ENCRYPTION_KEY=" + Fernet.generate_key().decode())
print("\n📝 Copy these to your .env file\n")
EOF
```

### Step 3: Configure Environment

Edit `.env` file:

```bash
# For Production
ENVIRONMENT=production
FORCE_HTTPS=true
FLASK_SECRET_KEY=<generated-key>
JWT_SECRET_KEY=<generated-key>
ENCRYPTION_KEY=<generated-key>

# For Development
ENVIRONMENT=development
FORCE_HTTPS=false
FLASK_SECRET_KEY=<generated-key>
JWT_SECRET_KEY=<generated-key>
ENCRYPTION_KEY=<generated-key>
```

### Step 4: Install New Dependencies

```bash
# Activate virtual environment if using one
source venv/bin/activate  # or: . venv/bin/activate

# Install new security dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python3 -c "from jose import jwt; from cryptography.fernet import Fernet; print('✅ Security libraries installed')"
```

### Step 5: Update Application

```bash
# Pull latest changes
git pull origin main  # or your branch

# Or if you have local changes
git stash
git pull origin main
git stash pop
```

### Step 6: Test Configuration

```bash
# Test that environment variables are loaded
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✅ FLASK_SECRET_KEY:', 'SET' if os.getenv('FLASK_SECRET_KEY') else '❌ NOT SET')
print('✅ JWT_SECRET_KEY:', 'SET' if os.getenv('JWT_SECRET_KEY') else '❌ NOT SET')
print('✅ ENCRYPTION_KEY:', 'SET' if os.getenv('ENCRYPTION_KEY') else '❌ NOT SET')
"
```

### Step 7: Start Application

```bash
# Start application
python3 start.py

# Or in daemon mode
python3 start.py --daemon

# Check logs for encryption messages
tail -f bot.log | grep -E "🔒|ENCRYPTION"
```

**Expected log messages:**
```
🔒 Encryption service available - secrets will be encrypted at rest
🔒 Bot and admin bot configurations saved to file (secrets encrypted)
```

### Step 8: Verify Migration

1. **Check web interface:** http://localhost:5000
2. **Verify bots still work:** Start a bot and send test message
3. **Check JWT endpoint:** 
   ```bash
   curl -X POST http://localhost:5000/api/v2/auth/token \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"your-password"}'
   ```
4. **Verify encryption:** Check `bot_configs.json` - tokens should look encrypted

---

## 🔐 Understanding Encryption

### What Gets Encrypted

Automatically encrypted fields:
- `telegram_token`
- `openai_api_key`
- `admin_password_hash`
- `jwt_secret_key`
- `api_key`
- `secret_key`
- `database_password`

### Encryption Format

Encrypted values look like:
```
gAAAAABhZXO...encrypted_data_here...xyZ==
```

### Backup Strategy

**IMPORTANT:** Keep your `ENCRYPTION_KEY` secure!
- Losing it = **Cannot decrypt existing configs**
- Store securely (password manager, secure vault)
- Rotate annually

**Backup recommendations:**
1. Backup `ENCRYPTION_KEY` separately from configs
2. Store in encrypted password manager
3. Document recovery process
4. Test decryption regularly

---

## 🚀 Production Deployment Checklist

- [ ] Generated secure random keys (FLASK_SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY)
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `FORCE_HTTPS=true`
- [ ] Configured reverse proxy (nginx/Apache) with SSL certificate
- [ ] Tested HTTPS redirect works
- [ ] Verified JWT token generation works
- [ ] Confirmed secrets are encrypted in `bot_configs.json`
- [ ] Created backup of `ENCRYPTION_KEY`
- [ ] Documented key storage location
- [ ] Tested bot functionality after migration
- [ ] Verified all existing bots still work
- [ ] Set up monitoring/alerting
- [ ] Configured log rotation (automatic, but verify)

---

## 🔄 Rollback Procedure

If something goes wrong:

### Option 1: Revert to Previous Version

```bash
# Stop application
python3 start.py --stop  # if running

# Restore backup
cp bot_configs.json.pre-3.8.3-backup bot_configs.json

# Checkout previous version
git checkout <previous-tag>

# Start application
python3 start.py
```

### Option 2: Disable Encryption

```bash
# Remove ENCRYPTION_KEY from .env
# Application will work with plaintext configs
# ⚠️ Not recommended for production
nano .env  # Comment out ENCRYPTION_KEY

# Restart
python3 start.py --stop
python3 start.py
```

---

## 📊 Migration Testing

### Test Scenario 1: Existing Bot

```bash
# 1. Verify bot config loads
curl http://localhost:5000/api/v1/bots

# 2. Start bot
curl -X POST http://localhost:5000/api/v1/bots/1/start

# 3. Send test message to bot
# (manual test in Telegram)

# 4. Verify bot responds
```

### Test Scenario 2: JWT Authentication

```bash
# 1. Get JWT token
TOKEN=$(curl -X POST http://localhost:5000/api/v2/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"your-password"}' \
     | jq -r '.access_token')

# 2. Verify token
curl -X POST http://localhost:5000/api/v2/auth/token/verify \
     -H "Authorization: Bearer $TOKEN"

# 3. Use token for API calls
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v2/system/status
```

### Test Scenario 3: Encryption

```bash
# 1. Check config file for encrypted values
grep "gAAAAAB" bot_configs.json && echo "✅ Encryption working" || echo "❌ Not encrypted"

# 2. Verify backup created
ls -lt bot_configs.json.backup_* | head -1

# 3. Check logs for encryption messages
grep "Encryption service" bot.log
```

---

## ❓ Troubleshooting

### Issue: "JWT not available"

**Solution:** Install python-jose
```bash
pip install python-jose[cryptography]
```

### Issue: "Encryption not available"

**Solution:** Install cryptography and set ENCRYPTION_KEY
```bash
pip install cryptography
# Add ENCRYPTION_KEY to .env (see Step 2)
```

### Issue: "Bot configs not loading"

**Solution:** Check encryption key matches
```bash
# Verify ENCRYPTION_KEY in .env matches the one used to encrypt
# If lost, restore from backup: bot_configs.json.pre-3.8.3-backup
```

### Issue: "HTTPS redirect loop"

**Solution:** Check reverse proxy configuration
```bash
# Ensure reverse proxy sets X-Forwarded-Proto header
# nginx example:
proxy_set_header X-Forwarded-Proto $scheme;
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `tail -f bot.log`
2. Review this guide carefully
3. Check GitHub Issues: https://github.com/ElectroNickP/Telegram-Bot-Manager/issues
4. Create new issue with:
   - Version migrating from
   - Error messages from logs
   - Steps to reproduce

---

## ✅ Post-Migration

After successful migration:

1. **Monitor logs** for first 24 hours
2. **Test all bots** with real messages
3. **Verify API endpoints** work correctly
4. **Document** any custom configurations
5. **Update** team documentation
6. **Schedule** first secret rotation (recommended: 90 days)

---

**Migration complete! Welcome to v3.8.3 🎉**

Your system is now production-ready with enterprise-grade security.


