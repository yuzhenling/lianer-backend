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
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }