"""
Feature Registry

Central registry for all features in the system.
Manages feature lifecycle, error isolation, and health monitoring.

For architecture details see: .meta/core/features/registry.md
"""

from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
import logging
import asyncio

from .base import Feature, FeatureMetadata

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """
    Feature registry
    
    - Registers features
    - Manages lifecycle (init, shutdown)
    - Isolates errors (non-critical feature failures don't crash app)
    - Provides health monitoring
    - Resolves dependencies
    
    Example:
        registry = FeatureRegistry()
        registry.register(UserSessionsFeature())
        registry.register(VoiceMessagesFeature())
        
        # Initialize all
        results = await registry.initialize_all()
        
        # Register handlers
        registry.register_telegram_handlers(dp, bot)
        registry.register_api_routes(app)
        
        # Health check
        health = await registry.health_check_all()
    """
    
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        """All registered features"""
        
        self.enabled_features: Set[str] = set()
        """Names of enabled features"""
        
        self.initialized_features: Set[str] = set()
        """Names of successfully initialized features"""
        
        self.failed_features: Dict[str, str] = {}
        """Names of failed features with error messages"""
        
        self._dependency_graph: Dict[str, List[str]] = defaultdict(list)
        """Feature dependency graph"""
    
    def register(self, feature: Feature) -> None:
        """
        Register a feature
        
        Args:
            feature: Feature instance
            
        Raises:
            ValueError: If feature with same name already registered
        """
        meta = feature.metadata()
        
        if meta.name in self.features:
            raise ValueError(f"Feature '{meta.name}' already registered")
        
        self.features[meta.name] = feature
        
        if meta.enabled:
            self.enabled_features.add(meta.name)
        
        # Build dependency graph
        for dep in meta.dependencies:
            self._dependency_graph[meta.name].append(dep)
        
        logger.info(
            f"✅ Registered feature: {meta.name} v{meta.version} "
            f"({'enabled' if meta.enabled else 'disabled'})"
        )
    
    def _resolve_initialization_order(self) -> List[str]:
        """
        Resolve feature initialization order based on dependencies
        
        Returns:
            List of feature names in initialization order
            
        Raises:
            ValueError: If circular dependency detected
        """
        # Topological sort (Kahn's algorithm)
        in_degree = defaultdict(int)
        
        for feature_name in self.enabled_features:
            for dep in self._dependency_graph[feature_name]:
                in_degree[feature_name] += 1
        
        queue = [
            name for name in self.enabled_features 
            if in_degree[name] == 0
        ]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Decrease in-degree for dependent features
            for feature_name, deps in self._dependency_graph.items():
                if current in deps:
                    in_degree[feature_name] -= 1
                    if in_degree[feature_name] == 0 and feature_name in self.enabled_features:
                        queue.append(feature_name)
        
        if len(result) != len(self.enabled_features):
            raise ValueError("Circular dependency detected in features")
        
        return result
    
    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all enabled features
        
        Features are initialized in dependency order.
        Non-critical feature failures don't stop initialization.
        Critical feature failures raise an exception.
        
        Returns:
            Dict mapping feature names to success status
            
        Raises:
            RuntimeError: If a critical feature fails to initialize
        """
        results = {}
        
        try:
            init_order = self._resolve_initialization_order()
        except ValueError as e:
            logger.error(f"❌ Failed to resolve feature dependencies: {e}")
            raise RuntimeError(f"Feature dependency error: {e}")
        
        logger.info(f"🔄 Initializing {len(init_order)} features in order: {init_order}")
        
        for name in init_order:
            feature = self.features[name]
            meta = feature.metadata()
            
            # Check dependencies
            missing_deps = [
                dep for dep in meta.dependencies
                if dep not in self.initialized_features
            ]
            
            if missing_deps:
                error_msg = f"Missing dependencies: {missing_deps}"
                logger.error(f"❌ {name}: {error_msg}")
                results[name] = False
                self.failed_features[name] = error_msg
                
                if meta.critical:
                    raise RuntimeError(f"Critical feature {name} failed: {error_msg}")
                
                continue
            
            # Initialize feature
            try:
                logger.info(f"🔄 Initializing {name}...")
                success = await feature.initialize()
                results[name] = success
                
                if success:
                    self.initialized_features.add(name)
                    logger.info(f"✅ {name} initialized successfully")
                else:
                    error_msg = "Initialization returned False"
                    logger.warning(f"⚠️  {name} failed to initialize")
                    self.failed_features[name] = error_msg
                    
                    if meta.critical:
                        raise RuntimeError(f"Critical feature {name} failed to initialize")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ {name} initialization error: {e}", exc_info=True)
                results[name] = False
                self.failed_features[name] = error_msg
                
                if meta.critical:
                    raise RuntimeError(f"Critical feature {name} failed: {e}")
        
        # Summary
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        logger.info(
            f"✅ Feature initialization complete: "
            f"{success_count}/{total_count} successful"
        )
        
        return results
    
    async def shutdown_all(self) -> None:
        """
        Gracefully shutdown all initialized features
        
        Shutdown happens in reverse initialization order.
        Errors during shutdown are logged but don't prevent other shutdowns.
        """
        # Shutdown in reverse order
        shutdown_order = list(reversed(list(self.initialized_features)))
        
        logger.info(f"🔄 Shutting down {len(shutdown_order)} features...")
        
        for name in shutdown_order:
            feature = self.features[name]
            
            try:
                await feature.shutdown()
                logger.info(f"✅ {name} shutdown complete")
            except Exception as e:
                logger.error(f"❌ {name} shutdown error: {e}", exc_info=True)
        
        self.initialized_features.clear()
        logger.info("✅ All features shutdown complete")
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """
        Register Telegram handlers for all initialized features
        
        Args:
            dp: Aiogram Dispatcher
            bot: Aiogram Bot instance
        """
        for name in self.initialized_features:
            feature = self.features[name]
            
            try:
                feature.register_telegram_handlers(dp, bot)
                logger.debug(f"✅ {name} handlers registered")
            except Exception as e:
                logger.error(f"❌ {name} handler registration error: {e}", exc_info=True)
    
    def register_api_routes(self, app) -> None:
        """
        Register API routes for all initialized features
        
        Args:
            app: Flask app instance
        """
        for name in self.initialized_features:
            feature = self.features[name]
            
            try:
                feature.register_api_routes(app)
                logger.debug(f"✅ {name} routes registered")
            except Exception as e:
                logger.error(f"❌ {name} route registration error: {e}", exc_info=True)
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all initialized features
        
        Returns:
            Dict with overall status and per-feature health:
                {
                    "overall_status": "healthy" | "degraded" | "unhealthy",
                    "features": {
                        "feature_name": {"status": "healthy", ...},
                        ...
                    },
                    "summary": {
                        "total": 5,
                        "healthy": 4,
                        "degraded": 1,
                        "unhealthy": 0
                    }
                }
        """
        feature_health = {}
        
        for name in self.initialized_features:
            feature = self.features[name]
            
            try:
                health = await feature.health_check()
                feature_health[name] = health
            except Exception as e:
                logger.error(f"❌ {name} health check error: {e}")
                feature_health[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Calculate summary
        statuses = [h.get("status", "unhealthy") for h in feature_health.values()]
        summary = {
            "total": len(statuses),
            "healthy": statuses.count("healthy"),
            "degraded": statuses.count("degraded"),
            "unhealthy": statuses.count("unhealthy"),
        }
        
        # Determine overall status
        if summary["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif summary["degraded"] > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "overall_status": overall_status,
            "features": feature_health,
            "summary": summary,
        }
    
    def get_feature(self, name: str) -> Optional[Feature]:
        """
        Get feature by name
        
        Args:
            name: Feature name
            
        Returns:
            Feature instance or None if not found
        """
        return self.features.get(name)
    
    def is_feature_enabled(self, name: str) -> bool:
        """Check if feature is enabled"""
        return name in self.enabled_features
    
    def is_feature_initialized(self, name: str) -> bool:
        """Check if feature is initialized"""
        return name in self.initialized_features
    
    def get_feature_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get info about all features
        
        Returns:
            Dict mapping feature names to info dicts
        """
        info = {}
        
        for name, feature in self.features.items():
            meta = feature.metadata()
            info[name] = {
                "version": meta.version,
                "description": meta.description,
                "dependencies": meta.dependencies,
                "enabled": meta.enabled,
                "critical": meta.critical,
                "tags": meta.tags,
                "initialized": name in self.initialized_features,
                "failed": name in self.failed_features,
                "error": self.failed_features.get(name),
            }
        
        return info


# Global singleton registry
feature_registry = FeatureRegistry()

