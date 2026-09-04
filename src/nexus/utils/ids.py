"""
Identifier generation utilities.
"""

from uuid import UUID, uuid4


def generate_id(prefix: str | None = None) -> str:
    """
    Generate a unique identifier.

    Args:
        prefix: Optional identifier prefix.

    Returns:
        A UUID-based identifier.
    """
    identifier = str(uuid4())

    if prefix:
        return f"{prefix}_{identifier}"

    return identifier


def generate_uuid() -> UUID:
    """Generate a UUID4 object."""
    return uuid4()