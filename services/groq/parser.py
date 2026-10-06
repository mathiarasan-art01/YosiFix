"""JSON response parsing and cleaning utilities for LLM output."""
import json
import re
import logging
from typing import Dict, Any
from services.groq.errors import SchemaValidationError

logger = logging.getLogger("yosifix.groq.parser")

_WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}

def clean_json_string(raw: str) -> str:
    """Strip markdown code blocks, repair common LLM slips, and extract JSON object."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]

    # Repair common LLM slips:
    # 1. Spelled-out decimal fraction: "0. nine" -> "0.9"
    for word, digit in _WORD_TO_DIGIT.items():
        text = re.sub(rf'0\.\s*{word}\b', f'0.{digit}', text, flags=re.IGNORECASE)
        text = re.sub(rf':\s*{word}\b', f': {digit}', text, flags=re.IGNORECASE)

    # 2. Trailing commas before closing braces or brackets: ", }" -> "}"
    text = re.sub(r',\s*([}\]])', r'\1', text)

    return text

def parse_json_response(raw: str) -> Dict[str, Any]:
    """Parse raw string into dictionary with fallback extraction and repair."""
    cleaned = clean_json_string(raw)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        raise SchemaValidationError("Top-level JSON response must be a dictionary")
    except json.JSONDecodeError as exc:
        logger.warning(f"Failed to parse JSON response: {exc}. Attempting relaxed repair...")
        match = re.search(r'(\{[\s\S]*\})', cleaned)
        if match:
            try:
                candidate = clean_json_string(match.group(1))
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        logger.error(f"Failed to parse JSON response: {exc}. Raw snippet: {raw[:200]}")
        raise SchemaValidationError(f"Invalid JSON response: {exc}") from exc

