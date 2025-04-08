# app/models/rhythm_settings.py
import enum


# 基础设置类型枚举
class SettingType(enum.Enum):
    DIFFICULTY = (1, "difficulty","难度")
    MEASURE_COUNT = (2, "measure_count","小节数量")
    TIME_SIGNATURE = (3, "time_signature","拍号")
    TEMPO = (4, "tempo","速度")
    TONALITY = (5, "tonality","调式")



