"""
Application configuration package.

Provides centralized settings, environment configuration,
and system constants for NEXUS-SENSE AI.
"""

from .settings import Settings, get_settings

__all__ = [
    "Settings",
    "get_settings",
]