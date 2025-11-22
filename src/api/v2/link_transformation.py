"""
API endpoints for Link Transformation management.

This module provides REST API endpoints for managing link-to-button
transformation rules and configurations.
"""

import logging
import uuid
from flask import Blueprint, request, jsonify

# Import the transformation classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from core.domain.link_transformation import (
        LinkTransformationConfig,
        LinkTransformationRule,
        LinkMatchType,
        create_google_script_rule,
        create_google_sheets_rule,
        create_github_rule,
        create_markdown_links_rule
    )
    from core.usecases.link_transformation import LinkTransformationService
    
    # Initialize service
    link_transformation_service = LinkTransformationService()
    LINK_TRANSFORMATION_AVAILABLE = True
    
except Exception as e:
    logging.warning(f"Link transformation not available: {e}")
    LINK_TRANSFORMATION_AVAILABLE = False
    link_transformation_service = None

# Import configuration manager for bot configs
import config_manager as cm

logger = logging.getLogger(__name__)

# Create blueprint
api_v2_link_transformation_bp = Blueprint('api_v2_link_transformation', __name__)


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/config', methods=['GET'])
def get_link_transformation_config(bot_id: int):
    """Get link transformation configuration for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
        
        # Get actual bot configuration from storage
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Get link transformation config or create default
        link_config_data = bot_config.get("config", {}).get("link_transformation", {})
        config = LinkTransformationConfig.from_dict(link_config_data)
        
        return jsonify({
            "success": True,
            "data": config.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting link transformation config for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/config', methods=['PUT'])
def update_link_transformation_config(bot_id: int):
    """Update link transformation configuration for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate and create config
        config = LinkTransformationConfig.from_dict(data)
        errors = config.validate()
        
        if errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": errors
            }), 400
        
        # Save to bot configuration
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Update the link transformation config in bot config
        bot_config["config"]["link_transformation"] = config.to_dict()
        
        # Save configuration
        cm.save_configs()
        logger.info(f"Link transformation config updated for bot {bot_id}")
        
        return jsonify({
            "success": True,
            "data": config.to_dict(),
            "message": "Configuration updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating link transformation config for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/rules', methods=['GET'])
def get_transformation_rules(bot_id: int):
    """Get all transformation rules for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        # Get from bot configuration
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Get transformation rules from config
        link_config_data = bot_config.get("config", {}).get("link_transformation", {})
        config = LinkTransformationConfig.from_dict(link_config_data)
        rules = config.transformation_rules
        
        return jsonify({
            "success": True,
            "data": [rule.to_dict() for rule in rules],
            "count": len(rules)
        })
        
    except Exception as e:
        logger.error(f"Error getting transformation rules for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/rules', methods=['POST'])
def create_transformation_rule(bot_id: int):
    """Create a new transformation rule for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Generate ID if not provided
        if 'id' not in data or not data['id']:
            data['id'] = str(uuid.uuid4())
        
        # Create and validate rule
        rule = LinkTransformationRule.from_dict(data)
        errors = rule.validate()
        
        if errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": errors
            }), 400
        
        # Add rule to bot configuration
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Get current link transformation config
        link_config_data = bot_config.get("config", {}).get("link_transformation", {})
        config = LinkTransformationConfig.from_dict(link_config_data)
        
        # Add new rule
        config.add_rule(rule)
        
        # Save back to bot config
        bot_config["config"]["link_transformation"] = config.to_dict()
        cm.save_configs()
        
        logger.info(f"Transformation rule created for bot {bot_id}: {rule.name}")
        
        return jsonify({
            "success": True,
            "data": rule.to_dict(),
            "message": "Rule created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating transformation rule for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/rules/<rule_id>', methods=['PUT'])
def update_transformation_rule(bot_id: int, rule_id: str):
    """Update a transformation rule for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Ensure ID matches
        data['id'] = rule_id
        
        # Create and validate rule
        rule = LinkTransformationRule.from_dict(data)
        errors = rule.validate()
        
        if errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": errors
            }), 400
        
        # Update rule in bot configuration
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Get current link transformation config
        link_config_data = bot_config.get("config", {}).get("link_transformation", {})
        config = LinkTransformationConfig.from_dict(link_config_data)
        
        # Update rule
        if not config.update_rule(rule_id, rule):
            return jsonify({
                "success": False,
                "error": f"Rule {rule_id} not found"
            }), 404
        
        # Save back to bot config
        bot_config["config"]["link_transformation"] = config.to_dict()
        cm.save_configs()
        
        logger.info(f"Transformation rule updated for bot {bot_id}: {rule.name}")
        
        return jsonify({
            "success": True,
            "data": rule.to_dict(),
            "message": "Rule updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating transformation rule {rule_id} for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/rules/<rule_id>', methods=['DELETE'])
def delete_transformation_rule(bot_id: int, rule_id: str):
    """Delete a transformation rule for a bot."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        # Remove rule from bot configuration
        bot_config = cm.get_bot_config(bot_id)
        if not bot_config:
            return jsonify({
                "success": False,
                "error": f"Bot {bot_id} not found"
            }), 404
        
        # Get current link transformation config
        link_config_data = bot_config.get("config", {}).get("link_transformation", {})
        config = LinkTransformationConfig.from_dict(link_config_data)
        
        # Remove rule
        if not config.remove_rule(rule_id):
            return jsonify({
                "success": False,
                "error": f"Rule {rule_id} not found"
            }), 404
        
        # Save back to bot config
        bot_config["config"]["link_transformation"] = config.to_dict()
        cm.save_configs()
        
        logger.info(f"Transformation rule deleted for bot {bot_id}: {rule_id}")
        
        return jsonify({
            "success": True,
            "message": "Rule deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting transformation rule {rule_id} for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/test', methods=['POST'])
def test_transformation(bot_id: int):
    """Test link transformation with sample text."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Text is required for testing"
            }), 400
        
        text = data['text']
        config_data = data.get('config', {})
        
        # Create config from provided data or get from bot
        if config_data:
            config = LinkTransformationConfig.from_dict(config_data)
        else:
            # Get from bot configuration
            bot_config = cm.get_bot_config(bot_id)
            if not bot_config:
                return jsonify({
                    "success": False,
                    "error": f"Bot {bot_id} not found"
                }), 404
            
            link_config_data = bot_config.get("config", {}).get("link_transformation", {})
            config = LinkTransformationConfig.from_dict(link_config_data)
        
        # Run transformation test
        preview = link_transformation_service.preview_transformation(text, config)
        
        return jsonify({
            "success": True,
            "data": preview
        })
        
    except Exception as e:
        logger.error(f"Error testing transformation for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/<int:bot_id>/rules/<rule_id>/test', methods=['POST'])
def test_rule(bot_id: int, rule_id: str):
    """Test a specific transformation rule against URLs."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({
                "success": False,
                "error": "URLs are required for testing"
            }), 400
        
        urls = data['urls']
        rule_data = data.get('rule')
        
        if not rule_data:
            return jsonify({
                "success": False,
                "error": "Rule data is required"
            }), 400
        
        # Create rule from provided data
        rule = LinkTransformationRule.from_dict(rule_data)
        
        # Test rule against each URL
        results = []
        for url in urls:
            matches = link_transformation_service.test_rule(rule, url)
            results.append({
                "url": url,
                "matches": matches
            })
        
        return jsonify({
            "success": True,
            "data": {
                "rule": rule.to_dict(),
                "test_results": results
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing rule {rule_id} for bot {bot_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/templates', methods=['GET'])
def get_rule_templates():
    """Get predefined rule templates."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        templates = [
            {
                "id": "markdown_links_template",
                "name": "Все Markdown ссылки",
                "description": "Автоматически преобразует все ссылки в формате [текст](url) в кнопки",
                "rule": create_markdown_links_rule().to_dict()
            },
            {
                "id": "google_script_template",
                "name": "Google Apps Script",
                "description": "Transform Google Apps Script links to buttons",
                "rule": create_google_script_rule().to_dict()
            },
            {
                "id": "google_sheets_template", 
                "name": "Google Sheets",
                "description": "Transform Google Sheets links to buttons",
                "rule": create_google_sheets_rule().to_dict()
            },
            {
                "id": "github_template",
                "name": "GitHub Repository",
                "description": "Transform GitHub links to buttons", 
                "rule": create_github_rule().to_dict()
            }
        ]
        
        return jsonify({
            "success": True,
            "data": templates
        })
        
    except Exception as e:
        logger.error(f"Error getting rule templates: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_v2_link_transformation_bp.route('/api/v2/link-transformation/match-types', methods=['GET'])
def get_match_types():
    """Get available match types for rules."""
    try:
        if not LINK_TRANSFORMATION_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Link transformation feature is not available"
            }), 503
            
        match_types = [
            {
                "value": LinkMatchType.MARKDOWN_LINK.value,
                "name": "Markdown ссылки",
                "description": "Все ссылки в формате [текст](url) в сообщении",
                "example": "[Оформить заказ](https://example.com)"
            },
            {
                "value": LinkMatchType.DOMAIN.value,
                "name": "Domain",
                "description": "Match by domain name (e.g., script.google.com)",
                "example": "script.google.com"
            },
            {
                "value": LinkMatchType.URL_CONTAINS.value,
                "name": "URL Contains",
                "description": "URL contains specific text",
                "example": "/spreadsheets/"
            },
            {
                "value": LinkMatchType.URL_REGEX.value,
                "name": "Regular Expression",
                "description": "Match using regex pattern",
                "example": r"github\.com\/[^\/]+\/[^\/]+"
            },
            {
                "value": LinkMatchType.FULL_URL.value,
                "name": "Exact URL",
                "description": "Exact URL match",
                "example": "https://example.com/specific-page"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": match_types
        })
        
    except Exception as e:
        logger.error(f"Error getting match types: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
