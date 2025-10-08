"""
Link Transformation Feature

Converts URLs in messages into interactive inline keyboard buttons.

For architecture details see: .meta/src/features/link_transformation/feature.md
"""

import logging
from typing import Dict, Any, Optional, List

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.features.base import Feature, FeatureMetadata
from core.domain.link_transformation import LinkTransformationConfig
from core.usecases.link_transformation import LinkTransformationService, TransformationResult

logger = logging.getLogger(__name__)


class LinkTransformationFeature(Feature):
    """
    Link Transformation Feature
    
    Automatically converts URLs in messages into clickable inline buttons:
    - Detects links in message text
    - Transforms them according to configured rules
    - Removes original links and replaces with buttons
    - Supports custom rules per domain/pattern
    
    This feature is isolated - link transformation errors don't affect other functionality.
    """
    
    def __init__(self):
        self.service: LinkTransformationService = None
        self._default_config: LinkTransformationConfig = None
    
    def metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            name="link_transformation",
            version="1.0.0",
            description="Transform URLs into interactive inline buttons",
            dependencies=[],
            enabled=True,
            critical=False,  # Non-critical
            tags=["telegram", "links", "buttons", "ui"]
        )
    
    async def initialize(self) -> bool:
        """
        Initialize link transformation service
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("🔄 Initializing link_transformation feature...")
            
            # Initialize service
            self.service = LinkTransformationService()
            
            # Create default config (disabled by default, enabled per bot config)
            self._default_config = LinkTransformationConfig(enabled=False)
            
            logger.info("✅ Link transformation feature initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize link_transformation feature: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> None:
        """
        Cleanup link transformation resources
        """
        try:
            logger.info("🔄 Shutting down link_transformation feature...")
            
            # Clear references
            self.service = None
            self._default_config = None
            
            logger.info("✅ Link transformation feature shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during link_transformation shutdown: {e}", exc_info=True)
    
    def process_message_for_links(
        self,
        text: str,
        config: LinkTransformationConfig
    ) -> TransformationResult:
        """
        Process message text for link transformation
        
        Args:
            text: Message text to process
            config: Link transformation configuration
            
        Returns:
            TransformationResult with processed text and buttons
        """
        if not self.service:
            logger.warning("Service not initialized")
            return TransformationResult(
                original_text=text,
                processed_text=text,
                buttons=[],
                transformations_count=0,
                matched_rules=[]
            )
        
        try:
            return self.service.process_message(text, config)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return TransformationResult(
                original_text=text,
                processed_text=text,
                buttons=[],
                transformations_count=0,
                matched_rules=[]
            )
    
    def create_inline_keyboard(
        self,
        buttons: List[Dict[str, str]],
        layout: str = "vertical"
    ) -> Optional[InlineKeyboardMarkup]:
        """
        Create Telegram inline keyboard from buttons
        
        Args:
            buttons: List of button dicts with 'text' and 'url'
            layout: Layout style ('vertical', 'horizontal', 'auto')
            
        Returns:
            InlineKeyboardMarkup or None if no buttons
        """
        if not buttons:
            return None
        
        try:
            keyboard_data = self.service.create_inline_keyboard(buttons, layout)
            
            # Convert to Aiogram InlineKeyboardMarkup
            keyboard = []
            for row in keyboard_data:
                keyboard_row = []
                for btn in row:
                    keyboard_row.append(
                        InlineKeyboardButton(text=btn["text"], url=btn["url"])
                    )
                keyboard.append(keyboard_row)
            
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
            
        except Exception as e:
            logger.error(f"Error creating inline keyboard: {e}", exc_info=True)
            return None
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """
        Register Telegram handlers
        
        Note: This feature doesn't register its own handlers directly.
        Instead, it provides methods that can be called from the main message
        handler when a message with links is detected.
        
        The main bot logic calls:
        - process_message_for_links() to transform text
        - create_inline_keyboard() to create buttons
        """
        logger.info("✅ Link transformation handlers available (inline mode)")
    
    def register_api_routes(self, app) -> None:
        """
        Register Flask API routes for link transformation management
        
        Args:
            app: Flask app instance
        """
        from flask import Blueprint, jsonify, request
        from flask_httpauth import HTTPBasicAuth
        
        bp = Blueprint('link_transformation', __name__, url_prefix='/api/v2/links')
        auth = HTTPBasicAuth()
        
        # Import auth
        try:
            from shared.auth import verify_credentials
            
            @auth.verify_password
            def verify_password(username, password):
                return verify_credentials(username, password)
                
        except Exception as e:
            logger.error(f"Failed to import auth: {e}")
            
            @auth.verify_password
            def verify_password(username, password):
                return False
        
        @bp.route('/preview', methods=['POST'])
        @auth.login_required
        def preview_transformation():
            """
            Preview link transformation without applying
            
            JSON body:
                text: Message text to preview
                config: LinkTransformationConfig dict
            
            Returns:
                Preview result with buttons
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
                
                text = data.get('text', '')
                config_data = data.get('config', {})
                
                # Parse config
                config = LinkTransformationConfig.from_dict(config_data)
                
                # Process
                result = self.service.preview_transformation(text, config)
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error previewing transformation: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/validate', methods=['POST'])
        @auth.login_required
        def validate_config():
            """
            Validate link transformation configuration
            
            JSON body:
                config: LinkTransformationConfig dict
            
            Returns:
                Validation errors (empty list if valid)
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
                
                config_data = data.get('config', {})
                config = LinkTransformationConfig.from_dict(config_data)
                
                errors = self.service.validate_configuration(config)
                
                return jsonify({
                    "valid": len(errors) == 0,
                    "errors": errors
                })
                
            except Exception as e:
                logger.error(f"Error validating config: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/test-rule', methods=['POST'])
        @auth.login_required
        def test_rule():
            """
            Test if a rule matches a specific URL
            
            JSON body:
                rule: LinkTransformationRule dict
                url: URL to test
            
            Returns:
                Whether rule matches URL
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
                
                from core.domain.link_transformation import LinkTransformationRule
                
                rule_data = data.get('rule', {})
                url = data.get('url', '')
                
                rule = LinkTransformationRule.from_dict(rule_data)
                matches = self.service.test_rule(rule, url)
                
                return jsonify({
                    "matches": matches,
                    "rule_name": rule.name,
                    "url": url
                })
                
            except Exception as e:
                logger.error(f"Error testing rule: {e}")
                return jsonify({"error": str(e)}), 500
        
        app.register_blueprint(bp)
        logger.info("✅ Link transformation API routes registered at /api/v2/links")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check feature health
        
        Returns:
            Health status dict
        """
        if not self.service:
            return {
                "status": "unhealthy",
                "reason": "Service not initialized"
            }
        
        try:
            # Test with a simple transformation
            test_text = "Test https://example.com link"
            test_config = LinkTransformationConfig(enabled=True)
            
            result = self.service.process_message(test_text, test_config)
            
            return {
                "status": "healthy",
                "details": {
                    "service_initialized": True,
                    "test_passed": True
                }
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "details": {
                    "service_initialized": self.service is not None
                }
            }

