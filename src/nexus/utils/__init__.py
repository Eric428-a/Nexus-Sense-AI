"""
Shared utility functions for NEXUS-SENSE AI.
"""

from .ids import generate_id
from .timestamps import utc_now

__all__ = [
    "generate_id",
    "utc_now",
]