# Phase 3: Functional Testing Plan & Results

**Date**: October 18, 2025  
**Status**: 🚀 Ready for Testing  
**Scope**: All bot commands, APIs, UI flows  

---

## 📋 Test Categories

### 1. **Bot Commands Testing** 🤖

#### 1.1 `/start` Command
- [ ] Send `/start` in private chat
- [ ] Expected: Bot responds with greeting
- [ ] Check logs for: `🚀 /start command received`
- [ ] Verify: Message sent successfully

**Test**:
```bash
# In Telegram:
/start

# Expected Response:
👋 Привет! Я бот [bot_name]. В личных сообщениях я отвечаю на всё...
```

#### 1.2 `/connect` Command (User Sessions Feature)
- [ ] Send `/connect` in private chat
- [ ] Expected: User session registered
- [ ] Check: UserSessionsFeature handler called
- [ ] Verify: User marked as online

**Test**:
```bash
# In Telegram:
/connect

# Expected:
✅ Session established
```

#### 1.3 `/exit` Command
- [ ] Send `/exit` in private chat
- [ ] Expected: User session ended
- [ ] Check: User marked as offline
- [ ] Verify: Bot stops responding to messages

**Test**:
```bash
# In Telegram:
/exit

# Expected:
👋 Session ended
```

#### 1.4 Voice Message Processing
- [ ] Send voice message
- [ ] Expected: Bot transcribes audio
- [ ] Check: OpenAI Whisper called
- [ ] Verify: Transcription text sent back

**Test**:
```
Action: Record & send voice message
Expected: Audio transcription received
```

#### 1.5 Text Messages (AI Responses)
- [ ] Send text message
- [ ] Expected: Bot responds with AI answer
- [ ] Check: OpenAI API called
- [ ] Verify: Response sent to user

**Test**:
```
Send: "Привет, как дела?"
Expected: AI response received
```

---

### 2. **API Endpoints Testing** 🔌

#### 2.1 System Health Check
```bash
curl -X GET http://localhost:5000/api/v2/system/health

Expected Response:
{
  "status": "healthy",
  "timestamp": "2025-10-18T...",
  "system": {
    "cpu": "...",
    "memory": "...",
    "disk": "..."
  },
  "bots": {...},
  "database": {...}
}
```

#### 2.2 Change Password API
```bash
curl -X POST http://localhost:5000/api/v2/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "admin",
    "new_password": "newpassword123"
  }'

Expected: 
{
  "success": true,
  "message": "Password changed successfully"
}
```

#### 2.3 Check Updates API
```bash
curl -X GET http://localhost:5000/api/check-updates

Expected:
{
  "has_updates": true/false,
  "current_version": "3.7.6",
  "latest_version": "...",
  "changelog": "..."
}
```

#### 2.4 Get Bots List
```bash
curl -X GET http://localhost:5000/api/v2/bots \
  -H "Authorization: Basic admin:admin"

Expected: Array of bot configurations
```

---

### 3. **UI Testing** 🖥️

#### 3.1 Login Page
- [ ] Navigate to http://localhost:5000/login
- [ ] Enter username: `admin`
- [ ] Enter password: `admin`
- [ ] Click "Login"
- [ ] Expected: Redirect to dashboard
- [ ] Verify: Session created

**Steps**:
```
1. Open http://localhost:5000/login
2. Username: admin
3. Password: admin  
4. Click Login button
5. Verify: Redirected to / (dashboard)
```

#### 3.2 Dashboard
- [ ] Check: All bots displayed
- [ ] Check: Stats working
- [ ] Check: Buttons visible (Home, Marketplace, API, Settings)
- [ ] Verify: No JS errors in console

**Checks**:
```
- Bot list visible
- Bot status shows correctly
- No console errors
- All navbar buttons work
```

#### 3.3 Settings Page
- [ ] Click "Settings" button
- [ ] Page loads: /settings
- [ ] Form visible with:
  - [ ] Current password field
  - [ ] New password field
  - [ ] Confirm password field
  - [ ] Change password button

**Steps**:
```
1. From dashboard, click "Settings"
2. URL should be /settings
3. See password change form
4. Fields: Current password, New password, Confirm
5. Change button visible
```

#### 3.4 Password Change UI
- [ ] Enter current password: `admin`
- [ ] Enter new password: `testpass123`
- [ ] Confirm new password: `testpass123`
- [ ] Click "Change Password"
- [ ] Expected: Success message
- [ ] Verify: .env file updated
- [ ] Test: Login with new password works

**Test**:
```
1. Current: admin
2. New: testpass123
3. Confirm: testpass123
4. Click button
5. Success message appears
6. Can login with: admin/testpass123
```

#### 3.5 Update Check Modal
- [ ] Click "Обновления" button
- [ ] Modal opens
- [ ] Shows "Проверка обновлений..."
- [ ] Checks for updates
- [ ] Shows result (есть/нет обновлений)
- [ ] If yes, shows changelog
- [ ] Has "Установить обновление" button

**Test**:
```
1. Click Updates button
2. Modal opens with spinner
3. Waits for check result
4. Shows: есть/нет обновлений
5. If yes: shows changelog
6. Install button visible
```

---

### 4. **Integration Testing** ⚙️

#### 4.1 Feature Registry Lifecycle
- [ ] All 3 features registered:
  - [ ] UserSessionsFeature ✅
  - [ ] VoiceMessagesFeature ✅
  - [ ] LinkTransformationFeature ✅
- [ ] All features initialized successfully
- [ ] Health check shows all healthy

**Check Logs**:
```
grep "Feature.*ready" src/bot.log
# Expected: 3 lines showing features ready
```

#### 4.2 Bot Message Flow
- [ ] Message received
- [ ] Command handlers check first
- [ ] Catch-all handler processes non-commands
- [ ] Feature handlers called in order
- [ ] Response sent back

**Test**:
```
Send: /start
Check: Command handler called first (not catch-all)
Send: hello
Check: Catch-all handler called (not command)
```

#### 4.3 Feature Handler Priority
- [ ] /connect goes to UserSessionsFeature (not catch-all)
- [ ] /exit goes to UserSessionsFeature (not catch-all)
- [ ] Regular messages go to catch-all (not feature handlers)
- [ ] No double-processing

**Verify in Logs**:
```
For /connect:
- Should see: "UserSessionsFeature: /connect handler"
- Should NOT see: "catch-all: processing /connect"
```

---

## 🧪 Manual Testing Procedures

### Setup
```bash
# 1. Start the app
cd /home/nick/Projects/Phuket/Telegram-Bot-Manager
python3 start.py

# 2. Wait for startup
sleep 5

# 3. Check health
curl http://localhost:5000/api/v2/system/health

# 4. Open in browser
# http://localhost:5000/login
```

### Test Bot Commands
```bash
# 1. Open Telegram
# 2. Find bot: @diosybot (or your bot name)
# 3. Test commands:
/start
/connect
/exit
[voice message]
[regular text]
```

### Test APIs
```bash
# 1. Check health
curl http://localhost:5000/api/v2/system/health

# 2. Change password
curl -X POST http://localhost:5000/api/v2/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{"current_password":"admin","new_password":"test123"}'

# 3. Check updates
curl http://localhost:5000/api/check-updates
```

### Test UI
```
1. Open: http://localhost:5000
2. Login: admin/admin
3. Check dashboard
4. Click Settings
5. Change password
6. Logout
7. Login with new password
8. Click "Обновления"
```

---

## 📊 Expected Test Results

### ✅ If All Pass

```
Bot Commands:         ✅ 5/5 working
API Endpoints:        ✅ 4/4 responding
UI Pages:             ✅ 5/5 loading
Integration:          ✅ 3/3 features ready
Security Fixes:       ✅ 3/3 applied
```

### ⚠️ If Issues Found

| Issue | Location | Fix |
|-------|----------|-----|
| `/start` not working | src/telegram_bot.py | Check Command filter |
| `/connect` not working | UserSessionsFeature | Check handler registration |
| Password change fails | API endpoint | Check .env permissions |
| UI errors | Browser console | Check JS errors |
| API 401 errors | Auth middleware | Check credentials |

---

## 🔍 Logs to Check

### Bot Logs
```bash
tail -f src/bot.log

# Look for:
- "✅ Feature 'user_sessions' ready"
- "✅ Feature 'voice_messages' ready"
- "✅ Feature 'link_transformation' ready"
- "/start command received"
- "/connect handler"
- "DEBUG: Incoming command: '/connect'"
```

### App Logs
```bash
tail -f logs/app.log

# Look for:
- "✅ Flask app created"
- "🔥 Global error handlers registered"
- "POST /api/v2/auth/change-password"
- No ERROR or CRITICAL messages
```

---

## ✅ Sign-Off Checklist

### Security Fixes
- [ ] FLASK_SECRET_KEY loaded from environment
- [ ] SESSION_COOKIE_SECURE respects environment
- [ ] ADMIN_PASSWORD_HASH required from .env
- [ ] No hardcoded secrets in code

### Bot Functionality
- [ ] `/start` command works
- [ ] `/connect` command works
- [ ] `/exit` command works
- [ ] Voice messages processed
- [ ] Text messages get AI responses
- [ ] No command conflicts

### API Endpoints
- [ ] /api/v2/system/health responds
- [ ] /api/v2/auth/change-password works
- [ ] /api/check-updates works
- [ ] Authentication required where needed

### UI/UX
- [ ] Login page works
- [ ] Dashboard renders
- [ ] Settings page loads
- [ ] Password change form works
- [ ] Update modal works
- [ ] No JS console errors

### Integration
- [ ] All 3 features initialized
- [ ] Feature handlers called correctly
- [ ] No double registration
- [ ] Error handling working

### Production Ready
- [ ] No CRITICAL errors in logs
- [ ] Health check passes
- [ ] All tests passing
- [ ] Security team sign-off pending

---

## 🎯 Next Steps After Testing

1. **If All Pass**:
   - ✅ Phase 3 complete
   - → Move to Phase 4: Production Readiness
   - → Fix remaining HIGH issues
   - → Deploy to staging

2. **If Issues Found**:
   - 📝 Document issues
   - 🔧 Apply fixes
   - ↩️ Re-run tests
   - → Continue until all pass

3. **Post-Testing**:
   - 📊 Generate test report
   - 📈 Update metrics
   - 📋 Update ISSUES_REGISTER.md
   - 🚀 Proceed to production

---

## 📝 Test Report Template

```
Test Date: [DATE]
Tester: [NAME]
Build: [VERSION]

RESULTS:
- Bot Commands: [PASS/FAIL] (X/5)
- API Endpoints: [PASS/FAIL] (X/4)
- UI Pages: [PASS/FAIL] (X/5)
- Integration: [PASS/FAIL] (3/3)

ISSUES FOUND:
1. [Issue description]
2. [Issue description]

RECOMMENDATION:
[PASS FOR PRODUCTION / NEEDS FIXES]
```

