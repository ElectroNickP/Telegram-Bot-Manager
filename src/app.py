#!/usr/bin/env python3
"""
Telegram Bot Manager - Refactored Application Factory

This is the new modularized version of the Flask application.
"""

import logging
import sys
import os
from datetime import timedelta
from flask import Flask, send_from_directory

# Import new modular components
from api.auth import auth_bp
from api.v1 import api_v1_bots_bp, api_v1_system_bp, api_v1_admin_bp, api_v1_marketplace_bp  
from api.v2 import api_v2_system_bp, api_v2_bots_bp, api_v2_telegram_bp
from api.v2.uploads import api_v2_uploads_bp
from api.v2.link_transformation import api_v2_link_transformation_bp
from web import web_bp
from shared.utils import datetime_filter, find_free_port

# Import configuration and bot managers
import config_manager as cm
import bot_manager as bm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory for Flask app"""
    # Load bot configurations from file
    logger.info("🔄 Loading bot configurations...")
    try:
        cm.load_configs()
        logger.info(f"📋 Loaded {len(cm.BOT_CONFIGS)} bot(s) from configuration file")
        
        # Auto-start all configured bots
        # Note: In a multi-worker Gunicorn setup, this would run in each worker.
        # We rely on Gunicorn running with 1 worker (and multiple threads) 
        # to prevent conflicting bot instances.
        bm.start_all_bots()
        logger.info("✅ Auto-start bots enabled")
        
    except Exception as e:
        logger.error(f"❌ Failed to load configurations: {e}")
        logger.info("📋 Continuing with empty configuration")
    
    app = Flask(__name__, template_folder="templates")
    
    # Security: Load secret key from environment or fallback to a generated one for this session
    # In production, ALWAYS set FLASK_SECRET_KEY
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-in-prod-" + os.urandom(12).hex())
    
    # Configure Jinja2 filters
    app.jinja_env.filters["datetime"] = datetime_filter
    
    # Add version to template context
    @app.context_processor
    def inject_version():
        try:
            from __version__ import FULL_VERSION
            return dict(app_version=FULL_VERSION)
        except ImportError:
            return dict(app_version="v3.8.3")

    # Session configuration
    app.config.update(
        SESSION_COOKIE_SECURE=False, # Set to True if using HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        SESSION_COOKIE_NAME="electronick_session"
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_v1_bots_bp)
    app.register_blueprint(api_v1_system_bp)
    app.register_blueprint(api_v1_admin_bp)
    app.register_blueprint(api_v1_marketplace_bp)
    app.register_blueprint(api_v2_system_bp)
    app.register_blueprint(api_v2_bots_bp)
    app.register_blueprint(api_v2_telegram_bp)
    app.register_blueprint(api_v2_uploads_bp)
    app.register_blueprint(api_v2_link_transformation_bp)
    
    # Add route for serving uploaded files
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files from uploads directory"""
        from pathlib import Path
        uploads_dir = Path(__file__).parent / 'static' / 'uploads'
        return send_from_directory(uploads_dir, filename)
    
    logger.info("✅ Flask app created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    # Use fixed port 5000 for production deployment
    port = 5000
    # Debug mode disabled for production to avoid process forking conflicts
    app.run(host="0.0.0.0", port=port, debug=False)
