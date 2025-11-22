"""
Test Plugin Loader
Verifies that plugin system loads/unloads correctly.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.loader import PluginLoader


def test_plugin_loader_init():
    """Test plugin loader initialization."""
    loader = PluginLoader(plugins_dir="plugins")
    assert loader.plugins_dir.name == "plugins"
    assert loader.loaded_plugins == {}
    assert loader.failed_plugins == []


def test_plugin_discovery():
    """Test plugin discovery."""
    loader = PluginLoader(plugins_dir="plugins")
    
    # Discover plugins
    plugins = loader.discover_plugins()
    
    # Should find at least template plugin
    assert len(plugins) > 0
    
    plugin_names = [p.name for p in plugins]
    assert "template" in plugin_names


def test_plugin_config_loading():
    """Test loading plugin config.json."""
    loader = PluginLoader(plugins_dir="plugins")
    
    # Load template config
    from pathlib import Path
    template_dir = Path("plugins/template")
    config = loader.load_plugin_config(template_dir)
    
    assert config is not None
    assert "enabled" in config
    assert "name" in config


def test_disabled_plugin_not_loaded():
    """Test that disabled plugins are not loaded."""
    loader = PluginLoader(plugins_dir="plugins")
    
    # Template plugin is disabled by default
    plugins = loader.load_all()
    
    # Template should not be loaded
    assert "template" not in plugins


def test_loader_stats():
    """Test loader statistics."""
    loader = PluginLoader(plugins_dir="plugins")
    loader.load_all()
    
    stats = loader.get_stats()
    
    assert "total_discovered" in stats
    assert "loaded" in stats
    assert "failed" in stats
    assert "plugin_names" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


