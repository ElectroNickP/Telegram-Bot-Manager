# Critical Path Smoke Test (QA)

This document defines the primary "Smoke Test" to verify the core functionality of the Telegram Bot Manager service. If this test fails, the service is considered **non-functional**.

## 1. Web Interface Access
- [ ] Open a browser and navigate to the service URL (e.g., `http://localhost:8000`).
- [ ] Verify that the user is redirected to the Login Page (if not logged in).

## 2. Authentication
- [ ] **Login Page**: Verify the login page loads correctly.
- [ ] **Login Action**: Enter valid credentials (`admin` / `securepassword123`) and click "Sign In".
- [ ] **Success**: Verify redirection to the **Dashboard** where the list of bots is visible.

## 3. Bot Creation & Validation
- [ ] Click the **"New Bot"** button.
- [ ] **Modal Persistence**: Verify that the modal **stays open** and does not close automatically. It should only close when "Create Bot" or "Cancel" is clicked.
- [ ] **Telegram Token Field**:
    - [ ] Enter a valid Telegram Bot Token.
    - [ ] **Validation**: The system should automatically validate the token.
    - [ ] **Auto-Fill**: The "Name" field should be automatically populated with the bot's name from Telegram.
- [ ] **OpenAI Assistant ID Field**:
    - [ ] Enter a valid OpenAI Assistant ID (e.g., `asst_...`).
    - [ ] **Validation**: The field should validate the format/existence (if possible).
- [ ] **OpenAI API Key Field**:
    - [ ] Enter a valid OpenAI API Key (e.g., `sk-...`).
    - [ ] **Validation**: The key should be verified.
- [ ] **Save**: Click "Create Bot".
- [ ] **Result**: The bot should be created and appear in the list with status **RUNNING**.

## 4. End-to-End Message Flow (The "Real" Test)
- [ ] Open the created bot in Telegram.
- [ ] Send a text message (e.g., "Hello").
- [ ] **System Action**:
    1.  **Receive**: The Worker service receives the update from Telegram.
    2.  **Process**: The system logs the incoming message.
    3.  **AI Request**: The system sends the message to the configured OpenAI Assistant (using the Thread ID).
    4.  **AI Response**: The system polls/waits for the Assistant's response.
    5.  **Send**: The system sends the AI's response back to the user in Telegram.
- [ ] **User Verification**: The user receives a relevant reply in Telegram.

## 5. Debugging & Logging
- [ ] Verify that the entire process above generates clear, traceable logs in the `worker` service.
- [ ] Logs should allow quick diagnosis of:
    - Invalid tokens.
    - OpenAI API errors.
    - Network timeouts.
    - Message processing failures.

---
**Status**: 
- [ ] Passed
- [ ] Failed
