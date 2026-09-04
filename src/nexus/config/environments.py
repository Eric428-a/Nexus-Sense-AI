"""
Environment definitions and environment-specific behavior.
"""

from enum import Enum


class Environment(str, Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


def is_development(environment: str) -> bool:
    """Return whether the environment is development."""
    return environment.lower() == Environment.DEVELOPMENT.value


def is_testing(environment: str) -> bool:
    """Return whether the environment is testing."""
    return environment.lower() == Environment.TESTING.value


def is_staging(environment: str) -> bool:
    """Return whether the environment is staging."""
    return environment.lower() == Environment.STAGING.value


def is_production(environment: str) -> bool:
    """Return whether the environment is production."""
    return environment.lower() == Environment.PRODUCTION.value