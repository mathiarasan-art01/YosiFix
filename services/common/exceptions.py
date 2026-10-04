"""Base application exceptions."""

class YosiFixException(Exception):
    """Base exception for all YosiFix operations."""
    pass

class StageExecutionError(YosiFixException):
    """Error during pipeline stage execution."""
    pass

class DependencyError(YosiFixException):
    """Error in pipeline stage dependency resolution."""
    pass

class ValidationError(YosiFixException):
    """Data contract or schema validation failure."""
    pass
