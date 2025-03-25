from typing import List

from pydantic import BaseModel

from app.models.pitch_setting import PitchBlackKey, PitchMode


class PitchRangeRequest(BaseModel):
    pitch_number_min: int
    pitch_number_max: int

class PitchSettingRequest(BaseModel):
    pitch_range: PitchRangeRequest
    include_pitch_black_keys: List[PitchBlackKey]
    mode: PitchMode