# app/models/rhythm_settings.py
import enum
from typing import Dict, Any


# 基础设置类型枚举
class MelodySettingType(enum.Enum):
    DIFFICULTY = (1, "difficulty","难度")
    MEASURE_COUNT = (2, "measure_count","小节数量")
    TIME_SIGNATURE = (3, "time_signature","拍号")
    TEMPO = (4, "tempo","速度")
    TONALITY = (5, "tonality","调式")


class Tonality(enum.Enum):
    # 大调 (Major)
    C = (1, "C大调", "C")
    G = (2, "G大调", "G")
    D = (3, "D大调", "D")
    A = (4, "A大调", "A")
    E = (5, "E大调", "E")
    B = (6, "B大调", "B")
    F_SHARP = (7, "升F大调", "F#")
    C_SHARP = (8, "升C大调", "C#")
    F = (9, "F大调", "F")
    B_FLAT = (10, "降B大调", "Bb")
    E_FLAT = (11, "降E大调", "Eb")
    A_FLAT = (12, "降A大调", "Ab")
    D_FLAT = (13, "降D大调", "Db")
    G_FLAT = (14, "降G大调", "Gb")
    C_FLAT = (15, "降C大调", "Cb")

    # 小调 (Minor)
    A_MINOR = (16, "a小调", "A")
    E_MINOR = (17, "e小调", "E")
    B_MINOR = (18, "b小调", "B")
    F_SHARP_MINOR = (19, "升f小调", "F#")
    C_SHARP_MINOR = (20, "升c小调", "C#")
    G_SHARP_MINOR = (21, "升g小调", "G#")
    D_SHARP_MINOR = (22, "升d小调", "D#")
    A_SHARP_MINOR = (23, "升a小调", "A#")
    D_MINOR = (24, "d小调", "D")
    G_MINOR = (25, "g小调", "G")
    C_MINOR = (26, "c小调", "C")
    F_MINOR = (27, "f小调", "F")
    B_FLAT_MINOR = (28, "降b小调", "Bb")
    E_FLAT_MINOR = (29, "降e小调", "Eb")
    A_FLAT_MINOR = (30, "降a小调", "Ab")

    def __init__(self, index, display_value, root_note):
        self._index = index
        self.display_value = display_value
        self.root_note = root_note

    def __str__(self):
        return self.display_value

    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self._index,
            "display_value": self.display_value
        }
    def get_root_note(self):
        return self.root_note
    def get_index(self):
        return self._index

class TonalityChoice(enum.Enum):
    # 大调 (Major)
    MAJOR_N = (1, "自然大调", [0, 2, 4, 5, 7, 9, 11])
    MAJOR_M = (2, "旋律大调", [0, 2, 4, 5, 7, 8, 11])
    MAJOR_C = (3, "和声大调", [0, 2, 4, 5, 7, 8, 10])#上行同自然

    MINOR_N = (4, "自然小调", [0, 2, 3, 5, 7, 8, 10])
    MINOR_M = (5, "旋律小调", [0, 2, 3, 5, 7, 8, 11])
    MINOR_C = (6, "和声小调", [0, 2, 3, 5, 7, 9, 11]) #下行：[0, 2, 3, 5, 7, 8, 10]

    def __init__(self, index, display_value, interval_nums):
        self._index = index
        self.display_value = display_value
        self.interval_nums = interval_nums

    def __str__(self):
        return self.display_value

    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self._index,
            "display_value": self.display_value
        }
    def get_interval_nums(self):
        return self.interval_nums

    def get_index(self):
        return self._index