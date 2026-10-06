"""Groq model configurations and fallback hierarchy."""
import os

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
FALLBACK_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
]

REASONING_MODELS = ("openai/gpt-oss",)

DEFAULT_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "30"))
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 4096

LANGUAGE_MAP = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
}
