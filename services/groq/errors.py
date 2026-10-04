"""Groq service custom exceptions."""

class GroqError(Exception):
    """Base exception for Groq service operations."""
    pass

class LLMError(GroqError):
    """Raised when Groq API encounters an error or model failure."""
    pass

class RateLimitError(GroqError):
    """Raised when Groq API rate limits requests."""
    pass

class AuthenticationError(GroqError):
    """Raised when Groq API key is invalid."""
    pass

class SchemaValidationError(GroqError):
    """Raised when Groq output fails schema validation."""
    pass
