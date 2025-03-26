# app/models/pitch_settings.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

from app.models.pitch import Pitch

@dataclass
class PitchRange:
    min: Pitch
    max: Pitch  # 最高音，如 "B4"
    list: List[Pitch]



class PitchBlackKey(Enum):
    C = ("C#","#C")
    D = ("D#","#D")
    F = ("F#","#F")
    G = ("G#","#G")
    A = ("A#","#A")
    def __init__(self, value, display_value):
        self._value = value
        self.display_value = display_value
    def __str__(self):
        return f"{self._value}" + ":" + f"{self.display_value}"

    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "value": self._value,  # 如 "C#"
            "display_value": self.display_value  # 如 "#C"
        }


class PitchMode(Enum):
    EFFICIENCY = (1, "效率")
    PITCH_PLUS = (2, "音阶+")
    STANDARD_PITCH = (3, "标准音+")
    PRACTICE = (4, "练习")
    def __init__(self, value, display_value):
        self._value = value
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "value": self._value,
            "display_value": self.display_value
        }

@dataclass
class PitchSingleSetting:
    pitch_range: PitchRange
    pitch_black_key: List[dict]
    mode: List[dict]


@dataclass
class PitchGroupSetting:
    pitch_range: PitchRange
    pitch_black_key: List[dict]
    count: List[int]
    tempo: List[int]
