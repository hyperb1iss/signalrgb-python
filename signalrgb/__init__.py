"""SignalRGB Python client library and CLI.

Provides both synchronous and asynchronous clients for the SignalRGB API,
alongside a Rich-powered Typer CLI.
"""

from .async_client import AsyncSignalRGBClient
from .client import (
    EffectIterator,
    SignalRGBClient,
)
from .exceptions import (
    APIError,
    ConnectionError,
    NotFoundError,
    SignalConnectionError,
    SignalRGBError,
    SignalRGBException,
)
from .model import (
    Effect,
    EffectPreset,
    Layout,
)

__version__ = "1.0.2"

__all__ = [
    "APIError",
    "AsyncSignalRGBClient",
    "ConnectionError",
    "Effect",
    "EffectIterator",
    "EffectPreset",
    "Layout",
    "NotFoundError",
    "SignalConnectionError",
    "SignalRGBClient",
    "SignalRGBError",
    "SignalRGBException",
    "__version__",
]
