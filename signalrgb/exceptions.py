"""
Exceptions for the SignalRGB API client.
"""

from .model import Error


class SignalRGBError(Exception):
    """Base exception for SignalRGB errors.

    This exception is raised when a general error occurs during API interactions.

    Attributes:
        message (str): The error message.
        error (Optional[Error]): The Error object containing additional error details.
    """

    def __init__(self, message: str, error: Error | None = None):
        super().__init__(message)
        self.error = error

    @property
    def code(self) -> str | None:
        """Optional[str]: The error code, if available."""
        return self.error.code if self.error else None

    @property
    def title(self) -> str | None:
        """Optional[str]: The error title, if available."""
        return self.error.title if self.error else None

    @property
    def detail(self) -> str | None:
        """Optional[str]: The detailed error message, if available."""
        return self.error.detail if self.error else None


class ConnectionError(SignalRGBError):
    """Exception raised for connection errors.

    This exception is raised when there's an issue connecting to the SignalRGB API.
    """


class APIError(SignalRGBError):
    """Exception raised for API errors.

    This exception is raised when the API returns an error response.
    """


class NotFoundError(SignalRGBError):
    """Exception raised when an item is not found.

    This exception is raised when trying to retrieve or apply a non-existent effect, preset, or layout.
    """


# For backward compatibility
SignalRGBException = SignalRGBError
# For backward compatibility
SignalConnectionError = ConnectionError
