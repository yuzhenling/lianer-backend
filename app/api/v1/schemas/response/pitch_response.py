from typing import List, Optional, Any

from pydantic import BaseModel

from app.models.pitch import Interval
from app.models.rhythm_settings import TimeSignature, RhythmDifficulty


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
    name: str
    simple_name: str
    pair: List[List[PitchResponse]]
    count: int
    is_three:bool
    type_id: int
    type_name: str
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

class PitchIntervalSettingResponse(BaseModel):
    answer_mode: List[dict[str, Any]]
    concordance_choice: List[dict[str, Any]]
    quality_choice: List[dict[str, Any]]
    play_mode: List[dict[str, Any]]
    interval_list: List[dict[str, Any]]
    fix_mode_enabled: bool
    fix_mode: List[dict[str, Any]]
    fix_mode_vals: List[str]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {}
    }

class IntervalQuestionResponse(BaseModel):
    id: int
    answer_id: int
    answer_name: str
    question: PitchIntervalPairResponse

class PitchIntervalExamResponse(BaseModel):
    exam_type: str
    question_num: int
    questions: List[IntervalQuestionResponse]
    correct_number: int = 0
    wrong_number: int = 0

class PitchChordSettingResponse(BaseModel):
    answer_mode: List[dict[str, Any]]
    play_mode: List[dict[str, Any]]
    chord_list: List[dict[str, Any]]
    transfer_set: List[dict[str, Any]]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "answer_mode": [
                        {
                            "index": 1,
                            "display_value": "听性质"
                        },
                        {
                            "index": 2,
                            "display_value": "听音高"
                        }
                    ],
                    "play_mode": [
                        {
                            "index": 1,
                            "display_value": "柱式"
                        },
                        {
                            "index": 2,
                            "display_value": "分解"
                        }
                    ],
                    "chord_list": [
                        {
                            "index": 1,
                            "name": "大三和弦",
                            "simple_name": "大三",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 2,
                            "name": "小三和弦",
                            "simple_name": "小三",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 3,
                            "name": "减三和弦",
                            "simple_name": "减三",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 4,
                            "name": "增三和弦",
                            "simple_name": "增三",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 5,
                            "name": "大七和弦",
                            "simple_name": "大七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 6,
                            "name": "小七和弦",
                            "simple_name": "小七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 7,
                            "name": "大小七和弦",
                            "simple_name": "大小七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 8,
                            "name": "小大七和弦",
                            "simple_name": "小大七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 9,
                            "name": "半减七和弦",
                            "simple_name": "半减七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 10,
                            "name": "减七和弦",
                            "simple_name": "减七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        },
                        {
                            "index": 11,
                            "name": "增大七和弦",
                            "simple_name": "增大七",
                            "type_id": 1,
                            "type_name": "三和弦"
                        }
                    ],
                    "transfer_set": [
                        {
                            "index": 1,
                            "display_value": "原位"
                        },
                        {
                            "index": 2,
                            "display_value": "一转位"
                        },
                        {
                            "index": 3,
                            "display_value": "二转位"
                        },
                        {
                            "index": 4,
                            "display_value": "三转位"
                        }
                    ]
                }
            ]

        }
    }


class ChordQuestionResponse(BaseModel):
    id: int
    answer_id: int
    answer_name: str
    question: List[PitchResponse]

class PitchChordExamResponse(BaseModel):
    exam_type: str
    question_num: int
    questions: List[ChordQuestionResponse]
    correct_number: int = 0
    wrong_number: int = 0
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "exam_type": "chord",
                    "question_num": 20,
                    "questions": [
                        {
                            "id": 1,
                            "answer_id": 5,
                            "answer_name": "大七",
                            "question": [
                                {
                                    "id": 37,
                                    "pitch_number": 37,
                                    "name": "A3",
                                    "alias": "null"
                                },
                                {
                                    "id": 41,
                                    "pitch_number": 41,
                                    "name": "C#4",
                                    "alias": "Db4"
                                },
                                {
                                    "id": 44,
                                    "pitch_number": 44,
                                    "name": "E4",
                                    "alias": "null"
                                },
                                {
                                    "id": 48,
                                    "pitch_number": 48,
                                    "name": "G#4",
                                    "alias": "Ab4"
                                }
                            ]
                        },
                        {
                            "id": 2,
                            "answer_id": 3,
                            "answer_name": "减三",
                            "question": [
                                {
                                    "id": 48,
                                    "pitch_number": 48,
                                    "name": "G#4",
                                    "alias": "Ab4"
                                },
                                {
                                    "id": 51,
                                    "pitch_number": 51,
                                    "name": "B4",
                                    "alias": "null"
                                },
                                {
                                    "id": 54,
                                    "pitch_number": 54,
                                    "name": "D5",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 3,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 16,
                                    "pitch_number": 16,
                                    "name": "C2",
                                    "alias": "null"
                                },
                                {
                                    "id": 19,
                                    "pitch_number": 19,
                                    "name": "D#2",
                                    "alias": "Eb2"
                                },
                                {
                                    "id": 23,
                                    "pitch_number": 23,
                                    "name": "G2",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 4,
                            "answer_id": 3,
                            "answer_name": "减三",
                            "question": [
                                {
                                    "id": 58,
                                    "pitch_number": 58,
                                    "name": "F#5",
                                    "alias": "Gb5"
                                },
                                {
                                    "id": 61,
                                    "pitch_number": 61,
                                    "name": "A5",
                                    "alias": "null"
                                },
                                {
                                    "id": 64,
                                    "pitch_number": 64,
                                    "name": "C6",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 5,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 39,
                                    "pitch_number": 39,
                                    "name": "B3",
                                    "alias": "null"
                                },
                                {
                                    "id": 42,
                                    "pitch_number": 42,
                                    "name": "D4",
                                    "alias": "null"
                                },
                                {
                                    "id": 46,
                                    "pitch_number": 46,
                                    "name": "F#4",
                                    "alias": "Gb4"
                                }
                            ]
                        },
                        {
                            "id": 6,
                            "answer_id": 4,
                            "answer_name": "增三",
                            "question": [
                                {
                                    "id": 72,
                                    "pitch_number": 72,
                                    "name": "G#6",
                                    "alias": "Ab6"
                                },
                                {
                                    "id": 76,
                                    "pitch_number": 76,
                                    "name": "C7",
                                    "alias": "null"
                                },
                                {
                                    "id": 80,
                                    "pitch_number": 80,
                                    "name": "E7",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 7,
                            "answer_id": 5,
                            "answer_name": "大七",
                            "question": [
                                {
                                    "id": 16,
                                    "pitch_number": 16,
                                    "name": "C2",
                                    "alias": "null"
                                },
                                {
                                    "id": 20,
                                    "pitch_number": 20,
                                    "name": "E2",
                                    "alias": "null"
                                },
                                {
                                    "id": 23,
                                    "pitch_number": 23,
                                    "name": "G2",
                                    "alias": "null"
                                },
                                {
                                    "id": 27,
                                    "pitch_number": 27,
                                    "name": "B2",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 8,
                            "answer_id": 3,
                            "answer_name": "减三",
                            "question": [
                                {
                                    "id": 48,
                                    "pitch_number": 48,
                                    "name": "G#4",
                                    "alias": "Ab4"
                                },
                                {
                                    "id": 51,
                                    "pitch_number": 51,
                                    "name": "B4",
                                    "alias": "null"
                                },
                                {
                                    "id": 54,
                                    "pitch_number": 54,
                                    "name": "D5",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 9,
                            "answer_id": 1,
                            "answer_name": "大三",
                            "question": [
                                {
                                    "id": 73,
                                    "pitch_number": 73,
                                    "name": "A6",
                                    "alias": "null"
                                },
                                {
                                    "id": 77,
                                    "pitch_number": 77,
                                    "name": "C#7",
                                    "alias": "Db7"
                                },
                                {
                                    "id": 80,
                                    "pitch_number": 80,
                                    "name": "E7",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 10,
                            "answer_id": 4,
                            "answer_name": "增三",
                            "question": [
                                {
                                    "id": 53,
                                    "pitch_number": 53,
                                    "name": "C#5",
                                    "alias": "Db5"
                                },
                                {
                                    "id": 57,
                                    "pitch_number": 57,
                                    "name": "F5",
                                    "alias": "null"
                                },
                                {
                                    "id": 61,
                                    "pitch_number": 61,
                                    "name": "A5",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 11,
                            "answer_id": 7,
                            "answer_name": "大小七",
                            "question": [
                                {
                                    "id": 19,
                                    "pitch_number": 19,
                                    "name": "D#2",
                                    "alias": "Eb2"
                                },
                                {
                                    "id": 23,
                                    "pitch_number": 23,
                                    "name": "G2",
                                    "alias": "null"
                                },
                                {
                                    "id": 26,
                                    "pitch_number": 26,
                                    "name": "A#2",
                                    "alias": "Bb2"
                                },
                                {
                                    "id": 29,
                                    "pitch_number": 29,
                                    "name": "C#3",
                                    "alias": "Db3"
                                }
                            ]
                        },
                        {
                            "id": 12,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 2,
                                    "pitch_number": 2,
                                    "name": "A#0",
                                    "alias": "Bb0"
                                },
                                {
                                    "id": 5,
                                    "pitch_number": 5,
                                    "name": "C#1",
                                    "alias": "Db1"
                                },
                                {
                                    "id": 9,
                                    "pitch_number": 9,
                                    "name": "F1",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 13,
                            "answer_id": 4,
                            "answer_name": "增三",
                            "question": [
                                {
                                    "id": 47,
                                    "pitch_number": 47,
                                    "name": "G4",
                                    "alias": "null"
                                },
                                {
                                    "id": 51,
                                    "pitch_number": 51,
                                    "name": "B4",
                                    "alias": "null"
                                },
                                {
                                    "id": 55,
                                    "pitch_number": 55,
                                    "name": "D#5",
                                    "alias": "Eb5"
                                }
                            ]
                        },
                        {
                            "id": 14,
                            "answer_id": 5,
                            "answer_name": "大七",
                            "question": [
                                {
                                    "id": 3,
                                    "pitch_number": 3,
                                    "name": "B0",
                                    "alias": "null"
                                },
                                {
                                    "id": 7,
                                    "pitch_number": 7,
                                    "name": "D#1",
                                    "alias": "Eb1"
                                },
                                {
                                    "id": 10,
                                    "pitch_number": 10,
                                    "name": "F#1",
                                    "alias": "Gb1"
                                },
                                {
                                    "id": 14,
                                    "pitch_number": 14,
                                    "name": "A#1",
                                    "alias": "Bb1"
                                }
                            ]
                        },
                        {
                            "id": 15,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 53,
                                    "pitch_number": 53,
                                    "name": "C#5",
                                    "alias": "Db5"
                                },
                                {
                                    "id": 56,
                                    "pitch_number": 56,
                                    "name": "E5",
                                    "alias": "null"
                                },
                                {
                                    "id": 60,
                                    "pitch_number": 60,
                                    "name": "G#5",
                                    "alias": "Ab5"
                                }
                            ]
                        },
                        {
                            "id": 16,
                            "answer_id": 7,
                            "answer_name": "大小七",
                            "question": [
                                {
                                    "id": 56,
                                    "pitch_number": 56,
                                    "name": "E5",
                                    "alias": "null"
                                },
                                {
                                    "id": 60,
                                    "pitch_number": 60,
                                    "name": "G#5",
                                    "alias": "Ab5"
                                },
                                {
                                    "id": 63,
                                    "pitch_number": 63,
                                    "name": "B5",
                                    "alias": "null"
                                },
                                {
                                    "id": 66,
                                    "pitch_number": 66,
                                    "name": "D6",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 17,
                            "answer_id": 7,
                            "answer_name": "大小七",
                            "question": [
                                {
                                    "id": 41,
                                    "pitch_number": 41,
                                    "name": "C#4",
                                    "alias": "Db4"
                                },
                                {
                                    "id": 45,
                                    "pitch_number": 45,
                                    "name": "F4",
                                    "alias": "null"
                                },
                                {
                                    "id": 48,
                                    "pitch_number": 48,
                                    "name": "G#4",
                                    "alias": "Ab4"
                                },
                                {
                                    "id": 51,
                                    "pitch_number": 51,
                                    "name": "B4",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 18,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 32,
                                    "pitch_number": 32,
                                    "name": "E3",
                                    "alias": "null"
                                },
                                {
                                    "id": 35,
                                    "pitch_number": 35,
                                    "name": "G3",
                                    "alias": "null"
                                },
                                {
                                    "id": 39,
                                    "pitch_number": 39,
                                    "name": "B3",
                                    "alias": "null"
                                }
                            ]
                        },
                        {
                            "id": 19,
                            "answer_id": 2,
                            "answer_name": "小三",
                            "question": [
                                {
                                    "id": 5,
                                    "pitch_number": 5,
                                    "name": "C#1",
                                    "alias": "Db1"
                                },
                                {
                                    "id": 8,
                                    "pitch_number": 8,
                                    "name": "E1",
                                    "alias": "null"
                                },
                                {
                                    "id": 12,
                                    "pitch_number": 12,
                                    "name": "G#1",
                                    "alias": "Ab1"
                                }
                            ]
                        },
                        {
                            "id": 20,
                            "answer_id": 6,
                            "answer_name": "小七",
                            "question": [
                                {
                                    "id": 62,
                                    "pitch_number": 62,
                                    "name": "A#5",
                                    "alias": "Bb5"
                                },
                                {
                                    "id": 65,
                                    "pitch_number": 65,
                                    "name": "C#6",
                                    "alias": "Db6"
                                },
                                {
                                    "id": 69,
                                    "pitch_number": 69,
                                    "name": "F6",
                                    "alias": "null"
                                },
                                {
                                    "id": 72,
                                    "pitch_number": 72,
                                    "name": "G#6",
                                    "alias": "Ab6"
                                }
                            ]
                        }
                    ],
                    "correct_number": 0,
                    "wrong_number": 0
                }
            ]
        }
    }

class RhythmNote(BaseModel):
    duration: float  # 音符时值：1.0=四分音符，0.5=八分音符，2.0=二分音符
    is_rest: bool = False  # 是否是休止符
    is_dotted: bool = False  # 是否是符点音符
    tied_to_next: bool = False  # 是否有连音线


class RhythmMeasure(BaseModel):
    notes: List[RhythmNote]


class RhythmScore(BaseModel):
    measures: List[List[RhythmMeasure]]
    time_signature: TimeSignature
    tempo: int
    is_correct: bool  # 标记是否是正确答案

class RhythmQuestionResponse(BaseModel):
    correct_answer: str  # A, B, C 或 D
    options: List[RhythmScore]
    tempo: int
    time_signature: TimeSignature
    measures_count: int
    difficulty: RhythmDifficulty
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "correct_answer": "A",
                    "options": [
                        {
                            "measures": [
                                [
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    }
                                ]
                            ],
                            "time_signature": "2/4",
                            "tempo": 80,
                            "is_correct": "true"
                        },
                        {
                            "measures": [
                                [
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1.5,
                                                "is_rest": "false",
                                                "is_dotted": "true",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    }
                                ]
                            ],
                            "time_signature": "2/4",
                            "tempo": 80,
                            "is_correct": "false"
                        },
                        {
                            "measures": [
                                [
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    }
                                ]
                            ],
                            "time_signature": "2/4",
                            "tempo": 80,
                            "is_correct": "false"
                        },
                        {
                            "measures": [
                                [
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "true",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    },
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            },
                                            {
                                                "duration": 1,
                                                "is_rest": "false",
                                                "is_dotted": "false",
                                                "tied_to_next": "false"
                                            }
                                        ]
                                    }
                                ]
                            ],
                            "time_signature": "2/4",
                            "tempo": 80,
                            "is_correct": "false"
                        }
                    ],
                    "tempo": 80,
                    "time_signature": "2/4",
                    "measures_count": 8,
                    "difficulty": "medium"
                }
            ]
        }
    }

class RhythmSettingResponse(BaseModel):
    difficulties: List[str]
    measures_counts: List[int]
    time_signatures: List[str]
    tempo: List[int]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "difficulties": [
                        "low",
                        "medium",
                        "high"
                    ],
                    "measures_counts": [
                        4,
                        6,
                        8,
                        10,
                        12,
                        16
                    ],
                    "time_signatures": [
                        "2/4",
                        "3/4",
                        "4/4",
                        "3/8",
                        "6/8"
                    ],
                    "tempo": [
                        40,
                        45,
                        50,
                        60,
                        80,
                        100
                    ]
                }
            ]
        }
    }

class MelodySettingResponse(RhythmSettingResponse):
    tonality: List[dict]
    tonality_choice: List[dict]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [

            ]
        }
    }

class MelodyQuestionResponse(BaseModel):
    correct_answer: str  # A, B, C 或 D
    options: List[RhythmScore]
    tempo: int
    time_signature: TimeSignature
    measures_count: int
    difficulty: RhythmDifficulty
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {}
    }

class MelodyQuestionResponse(BaseModel):
    correct_answer: str  # A, B, C 或 D
    options: List[RhythmScore]
    tempo: int
    time_signature: TimeSignature
    measures_count: int
    difficulty: RhythmDifficulty
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

class MelodyNotePitch(RhythmNote):
    pitch: PitchResponse

class MelodyMeasurePitch(BaseModel):
    notes: List[MelodyNotePitch]

class MelodyScorePitch(BaseModel):
    measures: List[List[MelodyMeasurePitch]]
    time_signature: TimeSignature
    tempo: int
    is_correct: bool  # 标记是否是正确答案

