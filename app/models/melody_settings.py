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
    C = (1, "C大调")
    G = (2, "G大调")
    D = (3, "D大调")
    A = (4, "A大调")
    E = (5, "E大调")
    B = (6, "B大调")
    F_SHARP = (7, "升F大调")
    C_SHARP = (8, "升C大调")
    F = (9, "F大调")
    B_FLAT = (10, "降B大调")
    E_FLAT = (11, "降E大调")
    A_FLAT = (12, "降A大调")
    D_FLAT = (13, "降D大调")
    G_FLAT = (14, "降G大调")
    C_FLAT = (15, "降C大调")

    # 小调 (Minor)
    A_MINOR = (16, "a小调")
    E_MINOR = (17, "e小调")
    B_MINOR = (18, "b小调")
    F_SHARP_MINOR = (19, "升f小调")
    C_SHARP_MINOR = (20, "升c小调")
    G_SHARP_MINOR = (21, "升g小调")
    D_SHARP_MINOR = (22, "升d小调")
    A_SHARP_MINOR = (23, "升a小调")
    D_MINOR = (24, "d小调")
    G_MINOR = (25, "g小调")
    C_MINOR = (26, "c小调")
    F_MINOR = (27, "f小调")
    B_FLAT_MINOR = (28, "降b小调")
    E_FLAT_MINOR = (29, "降e小调")
    A_FLAT_MINOR = (30, "降a小调")

    def __init__(self, index, display_value):
        self._index = index
        self.display_value = display_value

    def __str__(self):
        return self.display_value

    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self._index,
            "display_value": self.display_value
        }

class TonalityChoice(enum.Enum):
    # 大调 (Major)
    N = (1, "自然")
    M = (2, "旋律")
    C = (3, "和声")

    def __init__(self, index, display_value):
        self._index = index
        self.display_value = display_value

    def __str__(self):
        return self.display_value

    def to_dict(self) -> Dict[str, Any]:
        """返回包含所有值的字典"""
        return {
            "index": self._index,
            "display_value": self.display_value
        }