# Production Refactoring Summary

## Changes Made

1.  **Production Server**: Switched from Flask's built-in development server (`app.run()`) to **Gunicorn**, a production-grade WSGI server.
    -   **Reason**: `app.run()` is single-threaded (by default) and not secure for production. Gunicorn handles concurrent requests and process management much better.
    -   **Configuration**: `src/gunicorn_config.py` configured with 1 worker (to prevent bot polling conflicts) and 4 threads (to handle concurrent web requests).

2.  **Dependencies**: Updated `requirements-prod.txt` to include `gunicorn`.

3.  **Security**:
    -   Updated `src/app.py` to use `FLASK_SECRET_KEY` from environment variables.
    -   Added fallback key generation for safety.

4.  **Startup Scripts**:
    -   Updated `start-prod.py` to automatically install dependencies and start Gunicorn with the correct configuration.
    -   Created `generate_service.sh` to automatically generate a correct `systemd` service file for the current user and paths, fixing the issue with hardcoded `/root/` paths.

## How to Deploy

### 1. Quick Start (Manual)
Run the production starter script. It handles virtual environment creation and dependency installation automatically.
```bash
python3 start-prod.py
```

### 2. Systemd Service (Recommended)
Generate and install the service file to keep the bot running in the background and restart on boot.

```bash
# 1. Generate the service file for your user/path
chmod +x generate_service.sh
./generate_service.sh

# 2. Install and start
sudo cp telegram-bot-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-manager
sudo systemctl start telegram-bot-manager

# 3. Check status
sudo systemctl status telegram-bot-manager
```

## Maintenance

-   **Logs**: Check `bot.log` (application logs) or `journalctl -u telegram-bot-manager` (system logs).
-   **Updates**: `git pull origin prod` then restart the service (`sudo systemctl restart telegram-bot-manager`).

