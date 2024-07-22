"""
Data models for the SignalRGB API client.

This module contains Pydantic models that represent various data structures
used in the SignalRGB API, including effects, responses, and error information.
These models are used to validate and structure the data received from and sent to the API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Attributes(BaseModel):
    """
    Attributes of an effect in SignalRGB.

    This class represents the various properties and capabilities of an effect.
    It includes details such as the effect's name, description, publisher, and various flags
    indicating the effect's capabilities.

    Attributes:
        description (Optional[str]): A description of the effect.
        developer_effect (bool): Indicates whether this is a developer-created effect.
        image (Optional[str]): URL or path to the effect's image, if available.
        name (str): The name of the effect.
        parameters (Dict[str, Any]): A dictionary of effect-specific parameters.
        publisher (Optional[str]): The publisher or creator of the effect.
        uses_audio (bool): Indicates whether the effect uses audio input.
        uses_input (bool): Indicates whether the effect uses user input.
        uses_meters (bool): Indicates whether the effect uses meter data.
        uses_video (bool): Indicates whether the effect uses video input.
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

    This class represents the URLs related to an effect, such as where to apply it
    or retrieve its details.

    Attributes:
        apply (Optional[str]): URL to apply the effect, if available.
        self (Optional[str]): URL of the effect itself, typically for retrieving its details.
    """

    apply: Optional[str] = Field(default=None, description="URL to apply the effect")
    self: Optional[str] = Field(default=None, description="URL of the effect itself")


class Effect(BaseModel):
    """
    Represents a single effect in SignalRGB.

    This class combines the attributes and links of an effect with its unique identifier.
    It provides a complete representation of an effect in the SignalRGB system.

    Attributes:
        attributes (Attributes): The attributes of the effect.
        id (str): Unique identifier of the effect.
        links (Links): Links associated with the effect.
        type (str): Type of the object, typically 'lighting'.
    """

    attributes: Attributes = Field(..., description="Attributes of the effect")
    id: str = Field(..., description="Unique identifier of the effect")
    links: Links = Field(..., description="Links associated with the effect")
    type: str = Field(..., description="Type of the object, typically 'lighting'")


class EffectList(BaseModel):
    """
    A list of effects in SignalRGB.

    This class is used to represent multiple effects, typically in API responses
    that return a collection of effects.

    Attributes:
        items (List[Effect]): A list of Effect objects.
    """

    items: List[Effect] = Field(default_factory=list, description="List of effects")


class Error(BaseModel):
    """
    Represents an error returned by the SignalRGB API.

    This class includes details about the error such as its code, title, and a detailed message.
    It is typically used when the API encounters an error during request processing.

    Attributes:
        code (Optional[str]): An error code, if provided by the API.
        detail (Optional[str]): A detailed error message explaining the issue.
        title (str): A brief title or summary of the error.
    """

    code: Optional[str] = Field(default=None, description="Error code")
    detail: Optional[str] = Field(default=None, description="Detailed error message")
    title: str = Field(..., description="Error title")


class SignalRGBResponse(BaseModel):
    """
    Base class for responses from the SignalRGB API.

    This class includes common fields found in all API responses. It serves as a base
    for more specific response types and provides a consistent structure for handling
    API responses.

    Attributes:
        api_version (str): The version of the API used for this response.
        id (int): A unique identifier for this response.
        method (str): The HTTP method used for the request that generated this response.
        params (Dict[str, Any]): Any parameters that were part of the request.
        status (str): The status of the response, typically 'ok' or 'error'.
        errors (List[Error]): A list of Error objects if any errors occurred.
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

    This class extends SignalRGBResponse and includes an additional field for
    the effect details.

    Attributes:
        data (Optional[Effect]): The details of the requested effect, if available.
    """

    data: Optional[Effect] = Field(default=None, description="Effect details")


class EffectListResponse(SignalRGBResponse):
    """
    Response model for requests that return a list of effects.

    This class extends SignalRGBResponse and includes an additional field for
    the list of effects.

    Attributes:
        data (Optional[EffectList]): The list of effects returned by the API, if available.
    """

    data: Optional[EffectList] = Field(default=None, description="List of effects")
