from pydantic import BaseModel
from typing import Any, Dict, List


class Attributes(BaseModel):
    description: str = None
    developer_effect: bool = False
    image: str = None
    name: str = None
    parameters: Dict[str, Any] = {}
    publisher: str = None
    uses_audio: bool = False
    uses_input: bool = False
    uses_meters: bool = False
    uses_video: bool = False


class Links(BaseModel):
    apply: str
    self: str


class Effect(BaseModel):
    attributes: Attributes
    id: str
    links: Links
    type: str


class EffectList(BaseModel):
    items: List[Effect] = []


class Error(BaseModel):
    code: str
    detail: str
    title: str


class SignalRGBResponse(BaseModel):
    api_version: str
    id: int
    method: str
    params: Dict[str, Any] = {}
    status: str
    errors: List[Error] = []


class EffectDetailsResponse(SignalRGBResponse):
    data: Effect = None


class EffectListResponse(SignalRGBResponse):
    data: EffectList = None
