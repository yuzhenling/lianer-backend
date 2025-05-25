from typing import List, Literal

from pydantic import BaseModel, Field

from app.models.melody_settings import Tonality
from app.models.pitch_setting import PitchBlackKey, PitchMode
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature, MeasureCount, Tempo


class PitchRangeRequest(BaseModel):
    pitch_number_min: int = Field(..., ge=1, le=88)
    pitch_number_max: int = Field(..., gt=1, le=88)
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

# class PitchSettingRequest(BaseModel):
#     pitch_range: PitchRangeRequest
#     pitch_black_keys: List[Literal['C#', 'D#', 'F#', 'G#', 'A#']] = None
#     mode_key: int = Field(..., gt=1, le=4)
#     model_config = {
#         "from_attributes": True,
#         "arbitrary_types_allowed": True,
#         "json_schema_extra": {
#
#         }
#     }

class PitchSettingRequest(BaseModel):
    pitch_range: PitchRangeRequest
    pitch_black_keys: List[str] = []
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "pitch_range": {
                    "pitch_number_min": 4,
                    "pitch_number_max": 12
                }
            }
        }
    }

class PitchGroupSettingRequest(PitchSettingRequest):
    count: int = Field(..., ge=2, le=10)
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "pitch_range": {
                    "pitch_number_min": 4,
                    "pitch_number_max": 12
                },
                "count": 2
            }
        }
    }

class PitchIntervalSettingRequest(BaseModel):
    answer_mode: int = Field(..., ge=1, le=3)
    play_mode: int = Field(..., ge=1, le=4)
    interval_list: List[int]
    fix_mode_enabled: bool = False
    fix_mode:int = Field(..., ge=1, le=3)
    fix_mode_val: str = ""
    black_key: bool = False
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "answer_mode": 1,
                "play_mode": 1,
                "interval_list": [1,2,3,4,5,6,7,8,9,10,11,12,13],
                "fix_mode_enabled": "false",
                "fix_mode":1,
                "fix_mode_vals": "",
                "black_key": "false"
            }
        }
    }

class PitchChordSettingRequest(BaseModel):
    answer_mode: int = Field(..., ge=1, le=2)
    play_mode: int = Field(..., ge=1, le=2)
    chord_list: List[int]
    transfer_set: int
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "answer_mode": 1,
                "play_mode": 1,
                "chord_list": [1,2,3,4,5,6,7],
                "transfer_set": 1
            }
        }
    }

class RhythmSettingRequest(BaseModel):
    difficulty: RhythmDifficulty
    time_signature: TimeSignature = TimeSignature.TWO_FOUR
    measures_count: MeasureCount = MeasureCount.FOUR
    tempo: Tempo = Tempo.EIGHTY

class MelodySettingRequest(BaseModel):
    difficulty: RhythmDifficulty
    time_signature: TimeSignature = TimeSignature.TWO_FOUR
    measures_count: MeasureCount = MeasureCount.FOUR
    tempo: Tempo = Tempo.EIGHTY
    tonality: int = 1 # 调式 eg: C大调
    tonality_choice: int = 1 # 自然 旋律 和声
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "difficulty": "low",
                    "time_signature": "2/4",
                    "measures_count": 4,
                    "tempo": 80,
                    "tonality": 1,
                    "tonality_choice": 1
                }
            ]
        }
    }