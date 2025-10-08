"""
Feature System

Feature-based architecture for modular, isolated, testable features.

For architecture details see: .meta/core/features/__init__.md
"""

from .base import Feature, FeatureMetadata
from .registry import FeatureRegistry, feature_registry

__all__ = [
    "Feature",
    "FeatureMetadata",
    "FeatureRegistry",
    "feature_registry",
]

