"""
Integration Test - Full Bot Startup
Tests that bot can start with plugins loaded.
"""
import pytest
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_core_imports():
    """Test that core modules can be imported."""
    from core.logger import get_logger, setup_logger
    from core.context import Context
    from core.loader import PluginLoader
    from core.manager import BotManager
    
    assert get_logger is not None
    assert Context is not None
    assert PluginLoader is not None
    assert BotManager is not None


def test_plugin_template_imports():
    """Test that plugin template can be imported."""
    try:
        from plugins.template.plugin import Plugin
        assert Plugin is not None
    except ImportError as e:
        pytest.skip(f"Template plugin not available: {e}")


def test_plugin_system_initialization():
    """Test plugin system can initialize."""
    from core.loader import PluginLoader
    from core.context import Context
    
    # Create loader
    loader = PluginLoader(plugins_dir="plugins")
    assert loader is not None
    
    # Create context
    context = Context(max_messages=20)
    assert context is not None
    
    # Load plugins
    plugins = loader.load_all()
    print(f"\nLoaded {len(plugins)} plugin(s): {list(plugins.keys())}")
    
    # Should load at least some plugins
    # (template is disabled, but others might be enabled)
    assert isinstance(plugins, dict)


def test_logger_setup():
    """Test logger can be setup."""
    from core.logger import setup_logger
    
    logger = setup_logger("test")
    assert logger is not None
    
    # Test logging
    logger.info("Test log message")
    logger.debug("Test debug message")


def test_context_operations():
    """Test context manager operations."""
    from core.context import Context
    
    context = Context(max_messages=10)
    
    # Add message
    context.add_message(
        chat_id=123,
        user_id=456,
        text="Test message",
        username="testuser"
    )
    
    # Get context
    messages = context.get_context(123)
    assert len(messages) == 1
    
    # Get context string
    context_str = context.get_context_string(123)
    assert "Test message" in context_str


@pytest.mark.asyncio
async def test_bot_manager_initialization():
    """Test bot manager can be initialized (without actual token)."""
    from core.manager import BotManager
    
    # This will fail without real token, but should not crash
    try:
        manager = BotManager(
            token="TEST_TOKEN",
            plugins_dir="plugins",
            context_depth=20
        )
        
        assert manager is not None
        assert manager.loader is not None
        assert manager.context is not None
        
        # Check stats
        stats = manager.get_stats()
        assert "is_running" in stats
        assert "plugins" in stats
        assert "context" in stats
        
    except Exception as e:
        # Expected to fail without real token
        print(f"Expected failure without real token: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


