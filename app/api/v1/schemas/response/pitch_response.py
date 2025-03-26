from typing import List, Optional, Any

from pydantic import BaseModel
from sqlalchemy import null

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


class PitchSingleSettingResponse(BaseModel):
    pitch_range: PitchRangeResponse
    pitch_black_key: List[dict[str, str]]
    mode: List[dict[str, Any]]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "pitch_range": {
                    "min": {
                        "id": 216,
                        "pitch_number": 40,
                        "name": "C4",
                        "alias": "null"
                    },
                    "max": {
                        "id": 227,
                        "pitch_number": 51,
                        "name": "B4",
                        "alias": "null"
                    },
                    "list": [
                        {
                            "id": 216,
                            "pitch_number": 40,
                            "name": "C4",
                            "alias": "null"
                        },
                        {
                            "id": 217,
                            "pitch_number": 41,
                            "name": "C#4",
                            "alias": "Db4"
                        },
                        {
                            "id": 218,
                            "pitch_number": 42,
                            "name": "D4",
                            "alias": "null"
                        },
                        {
                            "id": 219,
                            "pitch_number": 43,
                            "name": "D#4",
                            "alias": "Eb4"
                        },
                        {
                            "id": 220,
                            "pitch_number": 44,
                            "name": "E4",
                            "alias": "null"
                        },
                        {
                            "id": 221,
                            "pitch_number": 45,
                            "name": "F4",
                            "alias": "null"
                        },
                        {
                            "id": 222,
                            "pitch_number": 46,
                            "name": "F#4",
                            "alias": "Gb4"
                        },
                        {
                            "id": 223,
                            "pitch_number": 47,
                            "name": "G4",
                            "alias": "null"
                        },
                        {
                            "id": 224,
                            "pitch_number": 48,
                            "name": "G#4",
                            "alias": "Ab4"
                        },
                        {
                            "id": 225,
                            "pitch_number": 49,
                            "name": "A4",
                            "alias": "null"
                        },
                        {
                            "id": 226,
                            "pitch_number": 50,
                            "name": "A#4",
                            "alias": "Bb4"
                        },
                        {
                            "id": 227,
                            "pitch_number": 51,
                            "name": "B4",
                            "alias": "null"
                        }
                    ]
                },
                "pitch_black_key": [
                    {
                        "value": "C#",
                        "display_value": "#C"
                    },
                    {
                        "value": "D#",
                        "display_value": "#D"
                    },
                    {
                        "value": "F#",
                        "display_value": "#F"
                    },
                    {
                        "value": "G#",
                        "display_value": "#G"
                    },
                    {
                        "value": "A#",
                        "display_value": "#A"
                    }
                ],
                "mode": [
                    {
                        "value": 1,
                        "display_value": "效率"
                    },
                    {
                        "value": 2,
                        "display_value": "音阶+"
                    },
                    {
                        "value": 3,
                        "display_value": "标准音+"
                    },
                    {
                        "value": 4,
                        "display_value": "练习"
                    }
                ]
            }
        }
    }

class Question(BaseModel):
    id: int
    pitch: PitchResponse  # 音高，如 "C4"

class SinglePitchExamResponse(BaseModel):
    exam_type: str
    question_num: int
    questions: List[Question]
    correct_number: int = 0
    wrong_number: int = 0


class PitchGroupSettingResponse(BaseModel):
    pitch_range: PitchRangeResponse
    pitch_black_key: List[dict[str, str]]
    count: List[int]
    tempo: List[int]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "pitch_range": {
                    "min": {
                        "id": 216,
                        "pitch_number": 40,
                        "name": "C4",
                        "alias": "null"
                    },
                    "max": {
                        "id": 227,
                        "pitch_number": 51,
                        "name": "B4",
                        "alias": "null"
                    },
                    "list": [
                        {
                            "id": 216,
                            "pitch_number": 40,
                            "name": "C4",
                            "alias": "null"
                        },
                        {
                            "id": 217,
                            "pitch_number": 41,
                            "name": "C#4",
                            "alias": "Db4"
                        },
                        {
                            "id": 218,
                            "pitch_number": 42,
                            "name": "D4",
                            "alias": "null"
                        },
                        {
                            "id": 219,
                            "pitch_number": 43,
                            "name": "D#4",
                            "alias": "Eb4"
                        },
                        {
                            "id": 220,
                            "pitch_number": 44,
                            "name": "E4",
                            "alias": "null"
                        },
                        {
                            "id": 221,
                            "pitch_number": 45,
                            "name": "F4",
                            "alias": "null"
                        },
                        {
                            "id": 222,
                            "pitch_number": 46,
                            "name": "F#4",
                            "alias": "Gb4"
                        },
                        {
                            "id": 223,
                            "pitch_number": 47,
                            "name": "G4",
                            "alias": "null"
                        },
                        {
                            "id": 224,
                            "pitch_number": 48,
                            "name": "G#4",
                            "alias": "Ab4"
                        },
                        {
                            "id": 225,
                            "pitch_number": 49,
                            "name": "A4",
                            "alias": "null"
                        },
                        {
                            "id": 226,
                            "pitch_number": 50,
                            "name": "A#4",
                            "alias": "Bb4"
                        },
                        {
                            "id": 227,
                            "pitch_number": 51,
                            "name": "B4",
                            "alias": "null"
                        }
                    ]
                },
                "pitch_black_key": [
                    {
                        "value": "C#",
                        "display_value": "#C"
                    },
                    {
                        "value": "D#",
                        "display_value": "#D"
                    },
                    {
                        "value": "F#",
                        "display_value": "#F"
                    },
                    {
                        "value": "G#",
                        "display_value": "#G"
                    },
                    {
                        "value": "A#",
                        "display_value": "#A"
                    }
                ],
                "count": [2,4,6,8,10],
                "tempo": [50.60, 70, 80, 90, 100, 110, 120]
            }
        }
    }
class GroupQuestionResponse(BaseModel):
    id: int
    pitches: List[PitchResponse]  # 音高，如 "C4"

class GroupPitchExamResponse(BaseModel):
    exam_type: str
    question_num: int
    questions: List[GroupQuestionResponse]
    correct_number: int = 0
    wrong_number: int = 0