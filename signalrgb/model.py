"""
Data models for the SignalRGB API client.

This module contains Pydantic models that represent various data structures
used in the SignalRGB API, including effects, responses, and error information.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Attributes(BaseModel):
    """
    Attributes of an effect in SignalRGB.

    This class represents the various properties and capabilities of an effect.
    """

    description: Optional[str] = Field(
        default=None, description="Description of the effect"
    )
    developer_effect: bool = Field(
        default=False, description="Whether this is a developer effect"
    )
    image: Optional[str] = Field(
        default=None, description="URL or path to the effect image"
    )
    name: str = Field(..., description="Name of the effect")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Effect parameters"
    )
    publisher: Optional[str] = Field(
        default=None, description="Publisher of the effect"
    )
    uses_audio: bool = Field(default=False, description="Whether the effect uses audio")
    uses_input: bool = Field(default=False, description="Whether the effect uses input")
    uses_meters: bool = Field(
        default=False, description="Whether the effect uses meters"
    )
    uses_video: bool = Field(default=False, description="Whether the effect uses video")


class Links(BaseModel):
    """
    Links associated with an effect in SignalRGB.

    This class represents the URLs related to an effect, such as where to apply it.
    """

    apply: Optional[str] = Field(default=None, description="URL to apply the effect")
    self: Optional[str] = Field(default=None, description="URL of the effect itself")


class Effect(BaseModel):
    """
    Represents a single effect in SignalRGB.

    This class combines the attributes and links of an effect with its unique identifier.
    """

    attributes: Attributes = Field(..., description="Attributes of the effect")
    id: str = Field(..., description="Unique identifier of the effect")
    links: Links = Field(..., description="Links associated with the effect")
    type: str = Field(..., description="Type of the object, typically 'lighting'")


class EffectList(BaseModel):
    """
    A list of effects in SignalRGB.

    This class is used to represent multiple effects, typically in API responses.
    """

    items: List[Effect] = Field(default_factory=list, description="List of effects")


class Error(BaseModel):
    """
    Represents an error returned by the SignalRGB API.

    This class includes details about the error such as its code, title, and a detailed message.
    """

    code: Optional[str] = Field(default=None, description="Error code")
    detail: Optional[str] = Field(default=None, description="Detailed error message")
    title: str = Field(..., description="Error title")


class SignalRGBResponse(BaseModel):
    """
    Base class for responses from the SignalRGB API.

    This class includes common fields found in all API responses.
    """

    api_version: str = Field(..., description="API version")
    id: int = Field(..., description="Response ID")
    method: str = Field(..., description="HTTP method used")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Request parameters"
    )
    status: str = Field(..., description="Response status")
    errors: List[Error] = Field(
        default_factory=list, description="List of errors if any"
    )


class EffectDetailsResponse(SignalRGBResponse):
    """
    Response model for requests that return details of a single effect.
    """

    data: Optional[Effect] = Field(default=None, description="Effect details")


class EffectListResponse(SignalRGBResponse):
    """
    Response model for requests that return a list of effects.
    """

    data: Optional[EffectList] = Field(default=None, description="List of effects")
