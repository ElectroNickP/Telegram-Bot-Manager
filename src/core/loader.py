"""
Plugin auto-loader.
Scans plugins/, loads only enabled ones.
Ignores disabled plugins (enabled: false in config.json).
"""
import importlib.util
import json
from pathlib import Path
from typing import Dict, List, Optional, Type

from core.logger import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """
    Automatic plugin loader with config-based enabling/disabling.
    
    Features:
    - Auto-scans plugins/ directory
    - Loads only enabled plugins (config.json: enabled=true)
    - Ignores disabled/missing configs
    - Hot-reload support (future)
    - Dependency resolution (future)
    
    Usage:
        loader = PluginLoader(plugins_dir="plugins")
        plugins = loader.load_all()
        
        for name, plugin_instance in plugins.items():
            plugin_instance.handle(message)
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize plugin loader.
        
        Args:
            plugins_dir: Directory containing plugins (default: "plugins")
        """
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins: Dict[str, any] = {}
        self.failed_plugins: List[str] = []
        
        logger.info(f"Plugin loader initialized (dir={self.plugins_dir})")
    
    def discover_plugins(self) -> List[Path]:
        """
        Discover all plugin directories.
        
        Returns:
            List of plugin directory paths
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []
        
        plugin_dirs = []
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # Check if it has plugin.py
                plugin_file = item / "plugin.py"
                if plugin_file.exists():
                    plugin_dirs.append(item)
        
        logger.info(f"Discovered {len(plugin_dirs)} plugin(s): {[p.name for p in plugin_dirs]}")
        return plugin_dirs
    
    def load_plugin_config(self, plugin_dir: Path) -> Optional[dict]:
        """
        Load plugin configuration from config.json.
        
        Args:
            plugin_dir: Path to plugin directory
        
        Returns:
            Config dict or None if not found/invalid
        """
        config_file = plugin_dir / "config.json"
        
        if not config_file.exists():
            logger.debug(f"No config.json for {plugin_dir.name}, assuming disabled")
            return None
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Failed to load config for {plugin_dir.name}: {e}")
            return None
    
    def is_plugin_enabled(self, config: Optional[dict]) -> bool:
        """
        Check if plugin is enabled.
        
        Args:
            config: Plugin configuration dict
        
        Returns:
            True if enabled, False otherwise
        """
        if config is None:
            return False
        
        return config.get("enabled", False) is True
    
    def load_plugin_module(self, plugin_dir: Path) -> Optional[Type]:
        """
        Dynamically load plugin module.
        
        Args:
            plugin_dir: Path to plugin directory
        
        Returns:
            Plugin class or None if failed
        """
        plugin_file = plugin_dir / "plugin.py"
        plugin_name = plugin_dir.name
        
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get Plugin class
            if not hasattr(module, "Plugin"):
                logger.error(f"Plugin {plugin_name} has no 'Plugin' class")
                return None
            
            return module.Plugin
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}", exc_info=True)
            return None
    
    def load_plugin(self, plugin_dir: Path) -> Optional[any]:
        """
        Load single plugin if enabled.
        
        Args:
            plugin_dir: Path to plugin directory
        
        Returns:
            Plugin instance or None if disabled/failed
        """
        plugin_name = plugin_dir.name
        
        # Load config
        config = self.load_plugin_config(plugin_dir)
        
        # Check if enabled
        if not self.is_plugin_enabled(config):
            logger.debug(f"Plugin {plugin_name} is disabled, skipping")
            return None
        
        # Load module
        PluginClass = self.load_plugin_module(plugin_dir)
        if PluginClass is None:
            self.failed_plugins.append(plugin_name)
            return None
        
        # Initialize plugin
        try:
            plugin_instance = PluginClass()
            
            # Call init method
            if hasattr(plugin_instance, "init"):
                plugin_instance.init()
            
            # Load config into plugin
            if hasattr(plugin_instance, "load_config"):
                plugin_instance.load_config(config)
            
            logger.info(f"✅ Loaded plugin: {plugin_name}")
            return plugin_instance
        
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin_name}: {e}", exc_info=True)
            self.failed_plugins.append(plugin_name)
            return None
    
    def load_all(self) -> Dict[str, any]:
        """
        Load all enabled plugins.
        
        Returns:
            Dictionary of {plugin_name: plugin_instance}
        """
        logger.info("🔄 Loading plugins...")
        
        plugin_dirs = self.discover_plugins()
        
        for plugin_dir in plugin_dirs:
            plugin_instance = self.load_plugin(plugin_dir)
            
            if plugin_instance:
                self.loaded_plugins[plugin_dir.name] = plugin_instance
        
        logger.info(f"✅ Loaded {len(self.loaded_plugins)} plugin(s)")
        
        if self.failed_plugins:
            logger.warning(f"⚠️  Failed to load: {', '.join(self.failed_plugins)}")
        
        return self.loaded_plugins
    
    def get_plugin(self, name: str) -> Optional[any]:
        """Get loaded plugin by name."""
        return self.loaded_plugins.get(name)
    
    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin (hot-reload).
        
        Args:
            name: Plugin name
        
        Returns:
            True if reloaded successfully
        """
        plugin_dir = self.plugins_dir / name
        
        if not plugin_dir.exists():
            logger.error(f"Plugin directory not found: {name}")
            return False
        
        # Unload old
        if name in self.loaded_plugins:
            del self.loaded_plugins[name]
        
        # Load new
        plugin_instance = self.load_plugin(plugin_dir)
        
        if plugin_instance:
            self.loaded_plugins[name] = plugin_instance
            logger.info(f"✅ Reloaded plugin: {name}")
            return True
        
        return False
    
    def get_stats(self) -> dict:
        """Get loader statistics."""
        return {
            "total_discovered": len(list(self.plugins_dir.iterdir())) if self.plugins_dir.exists() else 0,
            "loaded": len(self.loaded_plugins),
            "failed": len(self.failed_plugins),
            "plugin_names": list(self.loaded_plugins.keys())
        }


