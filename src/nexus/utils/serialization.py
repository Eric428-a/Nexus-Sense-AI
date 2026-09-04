"""
Serialization helpers.
"""

import json
from typing import Any


def to_json(
    value: Any,
    *,
    indent: int | None = None,
) -> str:
    """
    Serialize a Python object into JSON.
    """
    return json.dumps(
        value,
        indent=indent,
        ensure_ascii=False,
        default=str,
    )


def from_json(value: str) -> Any:
    """
    Deserialize a JSON string.
    """
    return json.loads(value)