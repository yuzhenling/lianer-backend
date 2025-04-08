# app/models/rhythm_settings.py
import enum


# 基础设置类型枚举
class SettingType(enum.Enum):
    DIFFICULTY = (1, "difficulty","难度")
    MEASURE_COUNT = (2, "measure_count","小节数量")
    TIME_SIGNATURE = (3, "time_signature","拍号")
    TEMPO = (4, "tempo","速度")


#难度
class RhythmDifficulty(str, enum.Enum):
    LOW = "low"  # 低难度：主要是四分音符、二分音符
    MEDIUM = "medium"  # 中等：加入八分音符
    HIGH = "high"  # 高难度：加入十六分音符、符点音符

#小节数量
class MeasureCount(int, enum.Enum):
    FOUR = 4
    SIX = 6
    EIGHT = 8
    TEN = 10
    TWELVE = 12
    SIXTEEN = 16

#拍号
class TimeSignature(enum.Enum):
    TWO_FOUR = "2/4"
    THREE_FOUR = "3/4"
    FOUR_FOUR = "4/4"
    THREE_EIGHT = "3/8"
    SIX_EIGHT = "6/8"


#速度
class Tempo(int, enum.Enum):
    FORTY = 40
    FORTY_FIVE = 45
    FIFTY = 50
    SIXTY = 60
    EIGHTY = 80
    HUNDRED = 100
