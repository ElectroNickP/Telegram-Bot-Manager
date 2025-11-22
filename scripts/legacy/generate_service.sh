#!/bin/bash
# Generator for systemd service file with correct paths

SERVICE_NAME="telegram-bot-manager"
USER=$(whoami)
GROUP=$(id -gn)
# Get absolute path to project root
PROJECT_ROOT=$(pwd)
PYTHON_EXEC="$PROJECT_ROOT/venv/bin/python"
GUNICORN_EXEC="$PROJECT_ROOT/venv/bin/gunicorn"

echo "Generating service file for user: $USER"
echo "Project root: $PROJECT_ROOT"

cat > $SERVICE_NAME.service << EOL
[Unit]
Description=Telegram Bot Manager - Professional Bot Management System
Documentation=https://github.com/ElectroNickP/Telegram-Bot-Manager
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$PROJECT_ROOT/src
Environment=PATH=$PROJECT_ROOT/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=$PROJECT_ROOT
Environment=FLASK_SECRET_KEY=$(openssl rand -hex 32)
ExecStart=$GUNICORN_EXEC -c gunicorn_config.py "app:create_app()"
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security settings
# NoNewPrivileges=true
# PrivateTmp=true
# ProtectSystem=full

# Resource limits
MemoryMax=1G
TasksMax=100

[Install]
WantedBy=multi-user.target
EOL

echo "✅ Generated $SERVICE_NAME.service"
echo "To install:"
echo "  sudo cp $SERVICE_NAME.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable $SERVICE_NAME"
echo "  sudo systemctl start $SERVICE_NAME"

