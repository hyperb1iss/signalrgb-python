"""Base package for signalrgb-python"""

from typing import Any, Literal, Optional, Union, cast

from .client import (
    APIError,
    ConnectionError,
    NotFoundError,
    SignalRGBClient,
    SignalRGBError,
)
from .model import (
    Effect,
    EffectPreset,
    Layout,
)

__version__ = "0.1.0"

__all__ = [
    "APIError",
    "ConnectionError",
    "Effect",
    "EffectPreset",
    "Layout",
    "NotFoundError",
    "SignalRGBClient",
    "SignalRGBError",
]
