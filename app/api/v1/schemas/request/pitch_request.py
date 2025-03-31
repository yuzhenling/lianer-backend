from typing import List, Literal

from pydantic import BaseModel, Field

from app.models.pitch_setting import PitchBlackKey, PitchMode


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

        }
    }

class PitchGroupSettingRequest(PitchSettingRequest):
    count: int = Field(..., ge=2, le=10)
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

class PitchIntervalSettingRequest(BaseModel):
    answer_mode: int = Field(..., ge=1, le=3)
    play_mode: int = Field(..., ge=1, le=4)
    interval_list: List[int]
    fix_mode_enabled: bool = False
    fix_mode:int = Field(..., ge=1, le=3)
    fix_mode_vals: List[str]
    black_key: bool = False
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }