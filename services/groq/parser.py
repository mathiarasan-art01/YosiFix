"""JSON response parsing and cleaning utilities for LLM output."""
import json
import logging
from typing import Dict, Any
from services.groq.errors import SchemaValidationError

logger = logging.getLogger("yosifix.groq.parser")

def clean_json_string(raw: str) -> str:
    """Strip markdown code blocks and excess whitespace around JSON."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end + 1]
    return text

def parse_json_response(raw: str) -> Dict[str, Any]:
    """Parse raw string into dictionary with fallback extraction."""
    cleaned = clean_json_string(raw)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        raise SchemaValidationError("Top-level JSON response must be a dictionary")
    except json.JSONDecodeError as exc:
        logger.warning(f"Failed to parse JSON response: {exc}. Raw snippet: {raw[:100]}")
        raise SchemaValidationError(f"Invalid JSON response: {exc}") from exc
