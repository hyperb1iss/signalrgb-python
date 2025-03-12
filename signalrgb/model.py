"""
Data models for the SignalRGB API client.

This module contains Mashumaro-based models that represent various data structures
used in the SignalRGB API, including effects, responses, and error information.
These models are used to validate and structure the data received from and sent to the API.
"""

from dataclasses import dataclass, field
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class Attributes(DataClassDictMixin):
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

    name: str
    description: str | None = None
    developer_effect: bool = False
    image: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    publisher: str | None = None
    uses_audio: bool = False
    uses_input: bool = False
    uses_meters: bool = False
    uses_video: bool = False


@dataclass
class Links(DataClassDictMixin):
    """
    Links associated with an effect in SignalRGB.

    This class represents the URLs related to an effect, such as where to apply it
    or retrieve its details.

    Attributes:
        apply (Optional[str]): URL to apply the effect, if available.
        self_link (Optional[str]): URL of the effect itself, typically for retrieving its details.
    """

    apply: str | None = None
    self_link: str | None = None

    class Config(BaseConfig):
        aliases = {"self_link": "self"}


@dataclass
class CurrentState(DataClassDictMixin):
    """
    Represents the current state of a SignalRGB instance.

    This class includes the current state of the instance, such as the current effect,
    whether the canvas is enabled, and the global brightness level.

    Attributes:
        name (str): The name of the current effect.
        enabled (bool): Indicates whether the canvas is currently enabled.
        global_brightness (int): The global brightness level of the canvas.
    """

    name: str | None = None
    enabled: bool = False
    global_brightness: int = 0


@dataclass
class CurrentStateHolder(DataClassDictMixin):
    """
    Holds the current state and metadata

    Attributes:
        attributes (Attributes): The attributes of the state.
        id (str): Unique identifier of the current effect.
        links (Links): Links associated with the current effect.
        type (str): Type of the object, typically 'effect'.
    """

    attributes: CurrentState
    id: str
    links: Links
    type: str


@dataclass
class Effect(DataClassDictMixin):
    """
    Represents a single effect in SignalRGB.

    This class combines the attributes and links of an effect with its unique identifier.
    It provides a complete representation of an effect in the SignalRGB system.

    Attributes:
        attributes (Attributes): The attributes of the effect.
        id (str): Unique identifier of the effect.
        links (Links): Links associated with the effect.
        type (str): Type of the object, typically 'effect'.
    """

    attributes: Attributes
    id: str
    links: Links
    type: str


@dataclass
class EffectList(DataClassDictMixin):
    """
    A list of effects in SignalRGB.

    This class is used to represent multiple effects, typically in API responses
    that return a collection of effects.

    Attributes:
        items (List[Effect]): A list of Effect objects.
    """

    items: list[Effect] = field(default_factory=list)


@dataclass
class Layout(DataClassDictMixin):
    """
    Represents a layout in SignalRGB.

    This class represents a layout, which is a configuration of devices and their positions.

    Attributes:
        id (str): The unique identifier of the layout.
        type (str): The type of the layout, typically 'layout'.
    """

    id: str
    type: str


@dataclass
class LayoutList(DataClassDictMixin):
    """
    A list of layouts in SignalRGB.

    This class is used to represent a layout, typically in API responses
    that return a collection of layouts.

    Attributes:
        items (List[Effect]): A list of Layout objects.
    """

    items: list[Layout] = field(default_factory=list)


@dataclass
class CurrentLayoutHolder(DataClassDictMixin):
    """
    Holds the current layout information.

    Attributes:
        current_layout (Layout): The current layout.
    """

    current_layout: Layout


@dataclass
class EffectPreset(DataClassDictMixin):
    """
    Represents a preset for an effect in SignalRGB.

    Attributes:
        id (str): The unique identifier of the preset.
        type (str): The type of the preset, typically 'preset'.
    """

    id: str
    type: str


@dataclass
class EffectPresetList(DataClassDictMixin):
    """
    A list of effect presets in SignalRGB.

    Attributes:
        id (str): The ID of the effect these presets belong to.
        items (List[EffectPreset]): A list of EffectPreset objects.
        type (str): The type of this object, typically 'presets'.
    """

    id: str
    items: list[EffectPreset] = field(default_factory=list)


@dataclass
class Error(DataClassDictMixin):
    """
    Represents an error returned by the SignalRGB API.

    This class includes details about the error such as its code, title, and a detailed message.
    It is typically used when the API encounters an error during request processing.

    Attributes:
        code (Optional[str]): An error code, if provided by the API.
        detail (Optional[str]): A detailed error message explaining the issue.
        title (str): A brief title or summary of the error.
    """

    title: str
    code: str | None = None
    detail: str | None = None


@dataclass
class SignalRGBResponse(DataClassDictMixin):
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

    api_version: str
    id: int
    method: str
    status: str
    params: dict[str, Any] = field(default_factory=dict)
    errors: list[Error] = field(default_factory=list)


@dataclass
class EffectDetailsResponse(SignalRGBResponse):
    """
    Response model for requests that return details of a single effect.

    This class extends SignalRGBResponse and includes an additional field for
    the effect details.

    Attributes:
        data (Optional[Effect]): The details of the requested effect, if available.
    """

    data: Effect | None = None


@dataclass
class CurrentStateResponse(SignalRGBResponse):
    """
    Response model for requests that return the current state of the canvas.

    This class extends SignalRGBResponse and includes an additional field for
    the current state of the canvas.

    Attributes:
        data (Optional[CurrentStateHolder]): The current state of the canvas, if available.
    """

    data: CurrentStateHolder | None = None


@dataclass
class EffectListResponse(SignalRGBResponse):
    """
    Response model for requests that return a list of effects.

    This class extends SignalRGBResponse and includes an additional field for
    the list of effects.

    Attributes:
        data (Optional[EffectList]): The list of effects returned by the API, if available.
    """

    data: EffectList | None = None


@dataclass
class LayoutListResponse(SignalRGBResponse):
    """
    Response model for requests that return a list of layouts.

    This class extends SignalRGBResponse and includes an additional field for
    the list of layouts.

    Attributes:
        data (Optional[Dict[str, Any]]): The data containing the list of layouts returned by the API, if available.
    """

    data: dict[str, Any] | None = None


@dataclass
class CurrentLayoutResponse(SignalRGBResponse):
    """
    Response model for requests that return the current layout.

    This class extends SignalRGBResponse and includes an additional field for
    the current layout.

    Attributes:
        data (Optional[CurrentLayoutHolder]): The data containing the current layout returned by the API, if available.
    """

    data: CurrentLayoutHolder | None = None


@dataclass
class EffectPresetListResponse(SignalRGBResponse):
    """
    Response model for requests that return a list of effect presets.

    Attributes:
        data (Optional[EffectPresetList]): The list of effect presets returned by the API, if available.
    """

    data: EffectPresetList | None = None


@dataclass
class EffectPresetResponse(SignalRGBResponse):
    """
    Response model for requests that return details of a single effect preset.

    Attributes:
        data (Optional[EffectPreset]): The details of the requested effect preset, if available.
    """

    data: EffectPreset | None = None
