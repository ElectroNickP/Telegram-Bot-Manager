"""
Marketplace routes for API v1
"""

import os
import sys
from flask import Blueprint, request, jsonify

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import configuration manager
import config_manager as cm

# Import logger
import logging
logger = logging.getLogger(__name__)

# Create blueprint
marketplace_bp = Blueprint('api_v1_marketplace', __name__, url_prefix='/api')


@marketplace_bp.route("/marketplace/bots", methods=["GET"])
def get_marketplace_bots_api():
    """Public API to get marketplace bots (no auth required)"""
    try:
        category = request.args.get("category")
        search = request.args.get("search", "").strip().lower()
        featured_only = request.args.get("featured") == "true"

        with cm.BOT_CONFIGS_LOCK:
            marketplace_bots = []
            for bot_entry in cm.BOT_CONFIGS.values():
                marketplace_config = bot_entry["config"].get("marketplace", {})
                if marketplace_config.get("enabled", False):
                    public_bot = {
                        "id": bot_entry["id"],
                        "title": marketplace_config.get("title", bot_entry["config"]["bot_name"]),
                        "description": marketplace_config.get("description", ""),
                        "category": marketplace_config.get("category", "other"),
                        "username": marketplace_config.get("username", ""),
                        "website": marketplace_config.get("website", ""),
                        "image_url": marketplace_config.get("image_url", ""),
                        "tags": marketplace_config.get("tags", []),
                        "featured": marketplace_config.get("featured", False),
                        "rating": marketplace_config.get("rating", 0.0),
                        "total_users": marketplace_config.get("total_users", 0),
                        "last_updated": marketplace_config.get("last_updated"),
                        "status": bot_entry.get("status", "unknown"),
                    }

                    # Apply filters
                    if category and public_bot["category"] != category:
                        continue

                    if featured_only and not public_bot["featured"]:
                        continue

                    if (
                        search
                        and search not in public_bot["title"].lower()
                        and search not in public_bot["description"].lower()
                    ):
                        continue

                    marketplace_bots.append(public_bot)

        # Sort by featured first, then by rating
        marketplace_bots.sort(key=lambda x: (not x["featured"], -x["rating"]))

        return jsonify({"success": True, "data": marketplace_bots, "total": len(marketplace_bots)})

    except Exception as e:
        logger.error(f"Error getting marketplace bots: {e}")
        return jsonify({"error": str(e)}), 500


@marketplace_bp.route("/marketplace/categories", methods=["GET"])
def get_marketplace_categories():
    """Get available bot categories"""
    categories = [
        {"id": "assistant", "name": "🤖 Ассистенты", "description": "Универсальные помощники"},
        {"id": "business", "name": "💼 Бизнес", "description": "Корпоративные решения"},
        {"id": "education", "name": "📚 Образование", "description": "Обучение и развитие"},
        {"id": "entertainment", "name": "🎮 Развлечения", "description": "Игры и досуг"},
        {
            "id": "productivity",
            "name": "⚡ Продуктивность",
            "description": "Повышение эффективности",
        },
        {"id": "support", "name": "🛠️ Поддержка", "description": "Техническая помощь"},
        {"id": "social", "name": "👥 Социальные", "description": "Общение и сообщества"},
        {"id": "news", "name": "📰 Новости", "description": "Информационные сервисы"},
        {"id": "finance", "name": "💰 Финансы", "description": "Финансовые услуги"},
        {"id": "health", "name": "🏥 Здоровье", "description": "Медицина и фитнес"},
        {"id": "travel", "name": "✈️ Путешествия", "description": "Туризм и поездки"},
        {"id": "food", "name": "🍕 Еда", "description": "Доставка и рецепты"},
        {"id": "other", "name": "📦 Другое", "description": "Прочие категории"},
    ]

    return jsonify({"success": True, "data": categories})



























