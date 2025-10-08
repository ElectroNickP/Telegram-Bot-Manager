"""
Base Feature Interface

Every feature in the system implements this interface.
This ensures consistent lifecycle, error isolation, and testability.

For architecture details see: .meta/core/features/base.md
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class FeatureMetadata:
    """
    Feature metadata
    
    Describes feature properties, dependencies, and criticality.
    """
    name: str
    """Unique feature name (e.g., 'user_sessions')"""
    
    version: str
    """Semantic version (e.g., '1.0.0')"""
    
    description: str
    """Human-readable description"""
    
    dependencies: List[str] = field(default_factory=list)
    """List of required feature names"""
    
    enabled: bool = True
    """Whether feature is enabled"""
    
    critical: bool = False
    """If True, failure blocks entire app"""
    
    tags: List[str] = field(default_factory=list)
    """Feature tags (e.g., ['telegram', 'api', 'paid'])"""


class Feature(ABC):
    """
    Base interface for all features
    
    Each feature:
    - Is isolated (bug in one doesn't affect others)
    - Has its own lifecycle (init, shutdown)
    - Can be enabled/disabled
    - Registers its own handlers/routes
    - Has health monitoring
    
    Example:
        class MyFeature(Feature):
            def metadata(self) -> FeatureMetadata:
                return FeatureMetadata(
                    name="my_feature",
                    version="1.0.0",
                    description="Does something cool",
                    enabled=True,
                    critical=False
                )
            
            async def initialize(self) -> bool:
                # Setup feature
                return True
            
            async def shutdown(self) -> None:
                # Cleanup
                pass
    """
    
    @abstractmethod
    def metadata(self) -> FeatureMetadata:
        """
        Feature metadata
        
        Returns:
            FeatureMetadata instance
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize feature
        
        Called during app startup. Should setup all necessary resources.
        
        Returns:
            True if initialization successful, False otherwise
            
        Raises:
            Exception: If feature is critical and fails
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Graceful shutdown
        
        Called during app shutdown. Should cleanup resources, close connections, etc.
        """
        pass
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """
        Register Telegram bot handlers (optional)
        
        Args:
            dp: Aiogram Dispatcher
            bot: Aiogram Bot instance
        """
        pass
    
    def register_api_routes(self, app) -> None:
        """
        Register Flask API routes (optional)
        
        Args:
            app: Flask app instance
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Feature health check
        
        Returns:
            Dict with keys:
                - status: "healthy" | "degraded" | "unhealthy"
                - details: Optional details about health state
                
        Example:
            {
                "status": "healthy",
                "details": {
                    "active_sessions": 5,
                    "storage_ok": True
                }
            }
        """
        return {"status": "healthy"}
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get JSON schema for feature configuration (optional)
        
        Returns:
            JSON schema dict or None
        """
        return None
    
    async def configure(self, config: Dict[str, Any]) -> bool:
        """
        Apply configuration (optional)
        
        Args:
            config: Configuration dict
            
        Returns:
            True if configuration applied successfully
        """
        return True

