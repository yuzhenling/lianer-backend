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


class AnswerMode(Enum):
    CONCORDANCE = (1, "听协和性")
    QUALITY = (2, "听性质")
    PITCH = (3, "听音高")

    def __init__(self, index, display_value):
        self.index = index
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }

class PlayMode(Enum):
    HARMONY = (1, "和声")
    UP = (2, "上行")
    DOWN = (3, "下行")
    UP_DOWN = (4, "上/下")

    def __init__(self, index, display_value):
        self.index = index
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }

@dataclass
class PitchIntervalSetting:
    answer_mode: List[AnswerMode]
    play_mode: int
    interval_list: List[dict[int, str]]
    fix: int
    tempo: List[int]
