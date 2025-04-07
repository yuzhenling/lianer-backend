# app/models/pitch_settings.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

from app.models.pitch import Pitch, PitchInterval


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
    def __index__(self):
        return self.index  # 返回枚举值
    def __display_value__(self):
        return self.display_value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }

class ConcordanceChoice(Enum):
    CONCORDANCE = (1, "完全协和")
    CONCORDANCE_PART = (2, "不完全协和")
    CONCORDANCE_NO = (3, "不协和")

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

class FixMode(Enum):
    ROOT_FIX = (1, "根音")
    TOP_FIX = (2, "冠音")
    RANDOM = (3, "随机")

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
    answer_mode: List[dict[str, Any]]
    concordance_choice: List[dict[str, Any]]
    quality_choice: List[dict[str, Any]]
    play_mode: List[dict[str, Any]]
    interval_list: List[dict[str, Any]]
    fix_mode_enabled: bool
    fix_mode: List[dict[str, Any]]
    fix_mode_vals: List[str]


class ChordAnswerMode(Enum):
    FIRST = (1, "听性质")
    SECOND = (2, "听音高")

    def __init__(self, index, display_value):
        self.index = index
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def __index__(self):
        return self.index  # 返回枚举值
    def __display_value__(self):
        return self.display_value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }

class ChordPlayMode(Enum):
    COMBINE = (1, "柱式")
    SINGLE = (2, "分解")

    def __init__(self, index, display_value):
        self.index = index
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def __index__(self):
        return self.index  # 返回枚举值
    def __display_value__(self):
        return self.display_value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }

class TransferSetMode(Enum):
    ORIGIN = (1, "原位")
    TRANSFER_1 = (2, "一转位")
    TRANSFER_2 = (3, "二转位")
    TRANSFER_3 = (4, "三转位")

    def __init__(self, index, display_value):
        self.index = index
        self.display_value = display_value
    def __str__(self):
        return self.value  # 返回枚举值
    def __index__(self):
        return self.index  # 返回枚举值
    def __display_value__(self):
        return self.display_value  # 返回枚举值
    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self.index,
            "display_value": self.display_value
        }



@dataclass
class PitchChordSetting:
    answer_mode: List[dict[str, Any]]
    play_mode: List[dict[str, Any]]
    chord_list: List[dict[str, Any]]
    transfer_set: List[dict[str, Any]]
