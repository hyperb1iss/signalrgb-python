from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum

class Attributes(BaseModel):
    description: Optional[str] = Field(default=None, description="Description of the effect")
    developer_effect: bool = Field(default=False, description="Whether this is a developer effect")
    image: Optional[str] = Field(default=None, description="URL or path to the effect image")
    name: str = Field(..., description="Name of the effect")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Effect parameters")
    publisher: Optional[str] = Field(default=None, description="Publisher of the effect")
    uses_audio: bool = Field(default=False, description="Whether the effect uses audio")
    uses_input: bool = Field(default=False, description="Whether the effect uses input")
    uses_meters: bool = Field(default=False, description="Whether the effect uses meters")
    uses_video: bool = Field(default=False, description="Whether the effect uses video")

class Links(BaseModel):
    apply: Optional[str] = Field(default=None, description="URL to apply the effect")
    self: Optional[str] = Field(default=None, description="URL of the effect itself")

class Effect(BaseModel):
    attributes: Attributes
    id: str = Field(..., description="Unique identifier of the effect")
    links: Links
    #type: str = Field(..., description="Type of the object")

class EffectList(BaseModel):
    items: List[Effect] = Field(default_factory=list, description="List of effects")

class Error(BaseModel):
    code: Optional[str] = Field(default=None, description="Error code")
    detail: Optional[str] = Field(default=None, description="Detailed error message")
    title: str = Field(..., description="Error title")

class SignalRGBResponse(BaseModel):
    api_version: str = Field(..., description="API version")
    id: int = Field(..., description="Response ID")
    method: str = Field(..., description="HTTP method used")
    params: Dict[str, Any] = Field(default_factory=dict, description="Request parameters")
    status: str = Field(..., description="Response status")
    errors: List[Error] = Field(default_factory=list, description="List of errors if any")

class EffectDetailsResponse(SignalRGBResponse):
    data: Optional[Effect] = Field(default=None, description="Effect details")

class EffectListResponse(SignalRGBResponse):
    data: EffectList = Field(..., description="List of effects")