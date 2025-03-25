from typing import List, Optional

from pydantic import BaseModel

from app.models.pitch import Interval
from app.models.pitch_setting import PitchBlackKey, PitchMode



class PitchResponse(BaseModel):
    id: int
    pitch_number: int
    name: str
    alias: Optional[str] = None
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "pitch_number": 40,
                "name": "C4",
                "alias": None,
                "url": ""
            }
        }
    }


class PitchGroupResponse(BaseModel):
    index: int
    name: str
    pitches: List[PitchResponse]
    count: int
    model_config = {
        "from_attributes": True,
    }

class PitchIntervalPairResponse(BaseModel):
    first: PitchResponse
    second: PitchResponse
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "first": {
                    "id": 40,
                    "pitch_number": 40,
                    "name": "C4",
                    "alias": None,
                    "url": ""
                },
                "second": {
                    "id": 44,
                    "pitch_number": 44,
                    "name": "E4",
                    "alias": None,
                    "url": ""
                }
            }
        }
    }


class PitchIntervalResponse(BaseModel):
    index: int
    interval: Interval
    semitones: int
    list: List[PitchIntervalPairResponse]
    count: int
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "index": 4,
                "interval": "major_third",
                "semitones": 4,
                "list": [
                    {
                        "first": {
                            "id": 40,
                            "pitch_number": 40,
                            "name": "C4",
                            "alias": None,
                            "url": ""
                        },
                        "second": {
                            "id": 44,
                            "pitch_number": 44,
                            "name": "E4",
                            "alias": None,
                            "url": ""
                        }
                    }
                ],
                "count": 1
            }
        }
    }


class PitchChordResponse(BaseModel):
    index: int
    value: str
    cn_value: str
    list: List[List[PitchResponse]]
    count: int
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

class PitchRangeResponse(BaseModel):
    min: PitchResponse
    max: PitchResponse  # 最高音，如 "B4"
    list: List[PitchResponse]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

class PitchSettingResponse(BaseModel):
    pitch_range: PitchRangeResponse
    pitch_black_key: List[PitchBlackKey]
    mode: List[PitchMode]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

