"""
Domain exceptions for Gravitational Singularity.
"""

class DomainError(Exception):
    """Base exception for all domain errors."""
    pass

class SyntaxValidationError(DomainError):
    """Raised when in-memory simulated patch violates syntax rules."""
    def __init__(self, message: str, file_path: str = "", line_number: int | None = None):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number

class PatchApplicationError(DomainError):
    """Raised when a diff patch cannot be applied to target content."""
    pass

class ModelInferenceError(DomainError):
    """Raised when local or cloud model invocation fails."""
    pass

class CompressionError(DomainError):
    """Raised when AST skeletonization or distillation fails."""
    pass
