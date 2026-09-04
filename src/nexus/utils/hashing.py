"""
Hashing utilities used for fingerprints, integrity checks,
and deterministic identifiers.
"""

import hashlib
from typing import Union


def sha256_hash(value: Union[str, bytes]) -> str:
    """
    Generate a SHA-256 hexadecimal digest.

    Args:
        value: String or bytes to hash.

    Returns:
        SHA-256 hexadecimal digest.
    """
    if isinstance(value, str):
        value = value.encode("utf-8")

    return hashlib.sha256(value).hexdigest()


def content_fingerprint(content: str) -> str:
    """
    Generate a stable fingerprint for textual content.
    """
    normalized = content.strip().replace("\r\n", "\n")
    return sha256_hash(normalized)