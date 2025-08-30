"""
API endpoints for link transformation management.

This module provides REST API endpoints for managing link-to-button
transformation rules and configurations.
"""

import logging
import uuid
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify
from functools import wraps

from core.domain.link_transformation import (
    LinkTransformationConfig,
    LinkTransformationRule,
    LinkMatchType,
    create_google_script_rule,
    create_google_sheets_rule,
    create_github_rule
)
from core.usecases.link_transformation import LinkTransformationService
from core.usecases.bot_management import BotManagementUseCase

logger = logging.getLogger(__name__)

# Create blueprint
link_transformation_bp = Blueprint('link_transformation', __name__, url_prefix='/api/v2/link-transformation')

# Initialize service
link_transformation_service = LinkTransformationService()


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement proper JWT authentication
        # For now, assume authenticated
        return f(*args, **kwargs)
    return decorated_function


@link_transformation_bp.route('/<int:bot_id>/config', methods=['GET'])
@require_auth
def get_link_transformation_config(bot_id: int):
    """Get link transformation configuration for a bot."""
    try:
        # TODO: Get from bot management use case
        # For now, return mock data
        config = LinkTransformationConfig()
        
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


@link_transformation_bp.route('/<int:bot_id>/config', methods=['PUT'])
@require_auth
def update_link_transformation_config(bot_id: int):
    """Update link transformation configuration for a bot."""
    try:
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
        
        # TODO: Save to bot configuration
        # For now, just return success
        
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


@link_transformation_bp.route('/<int:bot_id>/rules', methods=['GET'])
@require_auth
def get_transformation_rules(bot_id: int):
    """Get all transformation rules for a bot."""
    try:
        # TODO: Get from bot configuration
        # For now, return mock rules
        rules = [
            create_google_script_rule(),
            create_google_sheets_rule(),
            create_github_rule()
        ]
        
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


@link_transformation_bp.route('/<int:bot_id>/rules', methods=['POST'])
@require_auth
def create_transformation_rule(bot_id: int):
    """Create a new transformation rule for a bot."""
    try:
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
        
        # TODO: Add rule to bot configuration
        
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


@link_transformation_bp.route('/<int:bot_id>/rules/<rule_id>', methods=['PUT'])
@require_auth
def update_transformation_rule(bot_id: int, rule_id: str):
    """Update a transformation rule for a bot."""
    try:
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
        
        # TODO: Update rule in bot configuration
        
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


@link_transformation_bp.route('/<int:bot_id>/rules/<rule_id>', methods=['DELETE'])
@require_auth
def delete_transformation_rule(bot_id: int, rule_id: str):
    """Delete a transformation rule for a bot."""
    try:
        # TODO: Remove rule from bot configuration
        
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


@link_transformation_bp.route('/<int:bot_id>/test', methods=['POST'])
@require_auth
def test_transformation(bot_id: int):
    """Test link transformation with sample text."""
    try:
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
            # TODO: Get from bot configuration
            config = LinkTransformationConfig()
        
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


@link_transformation_bp.route('/<int:bot_id>/rules/<rule_id>/test', methods=['POST'])
@require_auth
def test_rule(bot_id: int, rule_id: str):
    """Test a specific transformation rule against URLs."""
    try:
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


@link_transformation_bp.route('/templates', methods=['GET'])
@require_auth
def get_rule_templates():
    """Get predefined rule templates."""
    try:
        templates = [
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


@link_transformation_bp.route('/match-types', methods=['GET'])
@require_auth
def get_match_types():
    """Get available match types for rules."""
    try:
        match_types = [
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









