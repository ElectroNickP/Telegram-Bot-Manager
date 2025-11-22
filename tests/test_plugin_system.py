"""
Test Plugin System
Integration tests for plugin loading and execution.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.context import Context, Message
from datetime import datetime


def test_context_add_message():
    """Test adding messages to context."""
    context = Context(max_messages=5)
    
    # Add messages
    context.add_message(
        chat_id=123,
        user_id=456,
        text="Hello",
        username="john"
    )
    
    # Get context
    messages = context.get_context(123)
    assert len(messages) == 1
    assert messages[0].text == "Hello"
    assert messages[0].username == "john"


def test_context_limit():
    """Test context message limit."""
    context = Context(max_messages=3)
    
    # Add more than limit
    for i in range(5):
        context.add_message(
            chat_id=123,
            user_id=456,
            text=f"Message {i}"
        )
    
    # Should only keep last 3
    messages = context.get_context(123)
    assert len(messages) == 3


def test_context_string_format():
    """Test context string formatting."""
    context = Context(max_messages=5)
    
    context.add_message(123, 456, "Hello", username="john")
    context.add_message(123, 789, "Hi there", username="jane")
    
    context_str = context.get_context_string(123)
    
    assert "john: Hello" in context_str
    assert "jane: Hi there" in context_str


def test_context_clear():
    """Test clearing context."""
    context = Context(max_messages=5)
    
    context.add_message(123, 456, "Hello")
    assert len(context.get_context(123)) == 1
    
    context.clear_context(123)
    assert len(context.get_context(123)) == 0


def test_context_stats():
    """Test context statistics."""
    context = Context(max_messages=5)
    
    context.add_message(123, 456, "Hello")
    context.add_message(456, 789, "Hi")
    
    stats = context.get_stats()
    
    assert stats["active_chats"] == 2
    assert stats["total_messages"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


