# services/groq/validator.py
"""Utility helpers for validating Groq responses.

At the moment the :class:`GroqClient` already validates against a Pydantic model.
This module exists for future extensions – e.g. checking confidence scores,
ensuring required fields are non‑empty, or applying custom business rules.
"""

from pydantic import BaseModel


def is_valid_instance(instance: BaseModel) -> bool:
    """Return ``True`` if the instance passes basic non‑empty checks.

    This can be expanded with domain‑specific validation later.
    """
    # Simple generic check – no field should be ``None`` or an empty string/list.
    for name, value in instance.dict().items():
        if value is None:
            return False
        if isinstance(value, (str, list, dict)) and not value:
            return False
    return True
