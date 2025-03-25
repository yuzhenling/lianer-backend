# app/models/pitch_settings.py

from enum import Enum
from pydantic import BaseModel

class PitchRange(BaseModel):
    lowest: str  # 最低音，如 "C4"
    highest: str  # 最高音，如 "B4"
    accidentals: list[str] = []  # 变化音，如 ["#C", "#D", "#F", "#G", "#A"]

class PitchMode(str, Enum):
    EFFICIENCY = "效率"
    PITCH_PLUS = "音阶+"
    STANDARD_PITCH = "标准音+"
    PRACTICE = "练习"



class PitchSettings(BaseModel):
    mode: PitchMode
    pitch_range: PitchRange