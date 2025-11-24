import os
import multiprocessing

# Gunicorn Configuration for Telegram Bot Manager

# Network
bind = "0.0.0.0:5000"

# Worker Processes
# CRITICAL: workers MUST be 1 because Telegram bots (aiogram) running inside the app 
# will conflict if multiple workers try to poll/connect with the same token.
workers = 1

# Threads per worker
# Use threads to handle concurrent web requests while the single worker manages the bots.
threads = 4

# Timeout
# Increase timeout for long-running operations
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process Name
proc_name = "telegram-bot-manager"

# Daemon mode is handled by systemd, so False here
daemon = False

