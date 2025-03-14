"""Base package for signalrgb-python"""

from typing import Any, Literal, Optional, Union, cast

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

__version__ = "1.0.0"  # Major version bump for async API

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
]
