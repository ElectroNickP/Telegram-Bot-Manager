# Environment Configuration Guide

## Security-Critical Setup

### 1. Flask Secret Key
```bash
# Generate a secure key (run once):
python3 -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"

# Add to .env:
FLASK_SECRET_KEY=<your-generated-key>
```

### 2. Admin Password Hash
```bash
# Generate SHA256 hash of your password:
python3 -c "import hashlib; print(hashlib.sha256(b'your_password').hexdigest())"

# Add to .env:
ADMIN_PASSWORD_HASH=<your-hash>
```

### 3. Production Environment
```bash
# For production, set:
FLASK_ENV=production
ENV=production

# This will:
# - Enable SESSION_COOKIE_SECURE (HTTPS only)
# - Disable Flask debug mode
# - Require proper secret key configuration
# - Refuse to use default passwords
```

### 4. Required Secrets
- `FLASK_SECRET_KEY` - Flask session encryption
- `ADMIN_PASSWORD_HASH` - Admin login credential
- `OPENAI_API_KEY` - OpenAI API access
- `TELEGRAM_BOT_TOKEN` - Telegram bot token

## Security Checklist

✅ Never commit .env to version control
✅ Set proper file permissions: `chmod 600 .env`
✅ Use environment variables for all secrets
✅ Rotate secrets regularly
✅ Enable SESSION_COOKIE_SECURE in production
✅ Set FLASK_ENV=production for production deployments

