"""Custom exception classes."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when user is not authorized to perform an action."""
    pass


class DuplicateError(Exception):
    """Raised when trying to create a resource that already exists."""
    pass
