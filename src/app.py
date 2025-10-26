#!/usr/bin/env python3
"""
Telegram Bot Manager - Refactored Application Factory

This is the new modularized version of the Flask application with feature-based architecture.
"""

import logging
import os
import sys
import secrets
from datetime import timedelta
from flask import Flask, send_from_directory, request, redirect
from logging.handlers import RotatingFileHandler

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

# MEDIUM-03: Import feature registry and features
# Note: Using parent directory for imports. For production, set PYTHONPATH properly.
# TODO: Refactor to use proper package structure (setup.py/pyproject.toml install)
try:
    # Try direct import first (if PYTHONPATH is set correctly)
    from core.features.registry import feature_registry
    from features import UserSessionsFeature, VoiceMessagesFeature, LinkTransformationFeature
    FEATURES_AVAILABLE = True
    logger_features = logging.getLogger(__name__)
    logger_features.info("✅ Feature system imports successful (app)")
except ImportError:
    # Fallback: Add parent directory to path (less preferred but works)
    try:
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from core.features.registry import feature_registry
        from features import UserSessionsFeature, VoiceMessagesFeature, LinkTransformationFeature
        FEATURES_AVAILABLE = True
        logger_features = logging.getLogger(__name__)
        logger_features.info("✅ Feature system imports successful (app - fallback path)")
    except Exception as e:
        logger_features = logging.getLogger(__name__)
        logger_features.error(f"❌ Feature system not available: {e}")
        FEATURES_AVAILABLE = False
        feature_registry = None

# Configure logging with rotation - MEDIUM-05 fix
log_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

# Create rotating file handler (max 10MB, keep 5 backup files)
file_handler = RotatingFileHandler(
    "bot.log", 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory for Flask app"""
    # Load bot configurations from file
    logger.info("🔄 Loading bot configurations...")
    try:
        cm.load_configs()
        logger.info(f"📋 Loaded {len(cm.BOT_CONFIGS)} bot(s) from configuration file")
        
        # Temporarily disable auto-starting bots to fix startup issues
        # TODO: Re-enable after fixing the startup flow
        # bm.start_all_bots()
        logger.info("⚠️ Auto-start bots disabled during startup troubleshooting")
        
    except Exception as e:
        logger.error(f"❌ Failed to load configurations: {e}")
        logger.info("📋 Continuing with empty configuration")
    
    app = Flask(__name__, template_folder="templates")
    
    # HIGH-01 Security Fix: Secret key from environment or generate secure random
    app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
    if app.secret_key == secrets.token_hex(32):
        logger.warning("⚠️ Using randomly generated secret key. Set FLASK_SECRET_KEY env variable for production!")
    
    # Configure Jinja2 filters
    app.jinja_env.filters["datetime"] = datetime_filter
    
    # Add version to template context
    @app.context_processor
    def inject_version():
        try:
            from __version__ import FULL_VERSION
            return dict(app_version=FULL_VERSION)
        except ImportError:
            return dict(app_version="v3.8.3 - Production Ready")

    # HIGH-01 Security Fix: Session configuration with HTTPS enforcement for production
    is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
    force_https = os.getenv('FORCE_HTTPS', 'true' if is_production else 'false').lower() == 'true'
    
    app.config.update(
        SESSION_COOKIE_SECURE=force_https,  # Only send cookie over HTTPS in production
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        SESSION_COOKIE_NAME="electronick_session"
    )
    
    # HIGH-01: HTTPS enforcement middleware for production
    if force_https:
        @app.before_request
        def enforce_https():
            """Redirect HTTP to HTTPS in production"""
            if not request.is_secure and request.headers.get('X-Forwarded-Proto', 'http') != 'https':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
        
        @app.after_request
        def add_security_headers(response):
            """Add security headers including HSTS"""
            # HSTS: Force HTTPS for 1 year
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            # Clickjacking protection
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            # Referrer policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            return response
        
        logger.info("🔒 HTTPS enforcement and security headers enabled for production")
    
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
    
    # Register feature API routes
    if FEATURES_AVAILABLE and feature_registry:
        try:
            logger.info("🔄 Registering feature API routes...")
            
            # Note: Features are already registered in telegram_bot.py
            # Here we just need to register their API routes if they exist
            
            # Check if features are already registered, if not register them
            if not feature_registry.features:
                feature_registry.register(UserSessionsFeature())
                feature_registry.register(VoiceMessagesFeature())
                feature_registry.register(LinkTransformationFeature())
            
            feature_registry.register_api_routes(app)
            logger.info("✅ Feature API routes registered")
            
        except Exception as e:
            logger.error(f"❌ Feature API route registration error: {e}", exc_info=True)
    
    # Add route for serving uploaded files
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files from uploads directory"""
        from pathlib import Path
        uploads_dir = Path(__file__).parent / 'static' / 'uploads'
        return send_from_directory(uploads_dir, filename)
    
    logger.info("✅ Flask app created with modular structure")
    logger.info("📋 Registered blueprints: auth, web, api_v1_bots, api_v1_system, api_v1_admin, api_v1_marketplace, api_v2_system, api_v2_bots, api_v2_telegram, api_v2_uploads, api_v2_link_transformation")
    logger.info("✅ API v1 completed!")
    logger.info("🚀 API v2 system module extracted!")
    logger.info("🚀 API v2 bots module extracted!")
    logger.info("🚀 API v2 telegram module extracted!")
    logger.info("🔗 API v2 link transformation module added!")
    logger.info("🎉 ALL API MODULES EXTRACTED! REFACTORING COMPLETE!")
    return app


if __name__ == "__main__":
    app = create_app()
    port = find_free_port(start_port=5000)
    # Disable reloader and debugger in this mode to avoid duplicate processes/signals
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
