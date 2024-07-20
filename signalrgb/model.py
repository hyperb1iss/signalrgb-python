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
    apply: str = None
    self: str = None


class Effect(BaseModel):
    attributes: Attributes
    id: str
    links: Links
    type: str


class EffectList(BaseModel):
    items: List[Effect] = []


class Error(BaseModel):
    code: str = None
    detail: str = None
    title: str = None


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
