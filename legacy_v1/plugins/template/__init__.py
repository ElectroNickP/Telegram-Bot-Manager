"""
Plugin Template - Copy this to create new plugins.

Usage:
    1. Copy this folder: cp -r plugins/template plugins/my_new_plugin
    2. Edit plugin.py - change class name and logic
    3. Edit config.json - enable and configure
    4. Restart bot - plugin will auto-load
"""

from .plugin import Plugin

__all__ = ["Plugin"]


