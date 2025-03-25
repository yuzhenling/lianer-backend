import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import os
from pathlib import Path
from app.db.base import Base
from typing import Dict, List
from pydantic import BaseModel
from app.utils.rename_file import ToneRenamer


class PitchType(str, enum.Enum):
    SINGLE_NOTE = "single_note"      # 单音测试
    INTERVAL = "interval"            # 音程测试
    CHORD = "chord"                  # 和弦测试
    MELODY = "melody"                # 旋律测试


class PitchTest(Base):
    __tablename__ = "pitch_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(SQLEnum(PitchType), default=PitchType.SINGLE_NOTE)
    
    # 测试内容
    target_note = Column(String)      # 目标音高（如 "C4", "G4-B4-D5"）
    user_recording = Column(String)    # 用户录音文件路径
    pitch_accuracy = Column(Float)     # 音高准确度（0-100）
    timing_accuracy = Column(Float)    # 节奏准确度（0-100，仅用于旋律测试）
    
    created_at = Column(DateTime, server_default=func.now())
    


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(SQLEnum(PitchType))
    
    # 练习数据
    duration = Column(Integer)         # 练习时长（秒）
    notes_practiced = Column(Integer)  # 练习音符数量
    average_accuracy = Column(Float)   # 平均准确度
    
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    # user = relationship("User", back_populates="practice_sessions")


class Pitch(Base):
    __tablename__ = "pitch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pitch_number = Column(Integer, nullable=False, unique=True)  # 钢琴键位号（1-88）
    name = Column(String(10), nullable=False)  # 主音名（如 A#0）
    alias = Column(String(10), nullable=True)  # 别名（如 Bb0）
    url = Column(String(255), nullable=False)  # 音频文件路径

    def isBlackKey(self):
        if self.alias:
            return True
        else:
            return False



# 音组模型
@dataclass
class PitchGroup:
    index: int
    name: str
    pitches: List[Pitch]
    count: int

PITCH_GROUP_NAMES = [
    "大字二组", "大字一组", "大字组",
    "小字组", "小字一组", "小字二组",
    "小字三组", "小字四组", "小字五组"
]

PITCH_GROUP_RANGES = [
    (1, 3),     # 大字二组: A0, A#0/Bb0, B0
    (4, 15),    # 大字一组: C1-B1
    (16, 27),   # 大字组: C2-B2
    (28, 39),   # 小字组: C3-B3
    (40, 51),   # 小字一组: C4-B4
    (52, 63),   # 小字二组: C5-B5
    (64, 75),   # 小字三组: C6-B6
    (76, 87),   # 小字四组: C7-B7
    (88, 88)    # 小字五组: C8
]


# 音程枚举
class Interval(str, enum.Enum):
    # 单音程
    MINOR_SECOND = "minor_second"  # 小二度
    MAJOR_SECOND = "major_second"  # 大二度
    MINOR_THIRD = "minor_third"    # 小三度
    MAJOR_THIRD = "major_third"    # 大三度
    PERFECT_FOURTH = "perfect_fourth"  # 纯四度
    TRITONE = "tritone"           # 增四度/减五度
    PERFECT_FIFTH = "perfect_fifth"   # 纯五度
    MINOR_SIXTH = "minor_sixth"    # 小六度
    MAJOR_SIXTH = "major_sixth"    # 大六度
    MINOR_SEVENTH = "minor_seventh"  # 小七度
    MAJOR_SEVENTH = "major_seventh"  # 大七度
    PERFECT_OCTAVE = "perfect_octave" # 纯八度

    # 复音程
    MINOR_NINTH = "minor_ninth"     # 小九度
    MAJOR_NINTH = "major_ninth"     # 大九度
    MINOR_TENTH = "minor_tenth"     # 小十度
    MAJOR_TENTH = "major_tenth"     # 大十度
    PERFECT_ELEVENTH = "perfect_eleventh"  # 纯十一度
    AUGMENTED_ELEVENTH = "augmented_eleventh"  # 增十一度
    PERFECT_TWELFTH = "perfect_twelfth"    # 纯十二度
    MINOR_THIRTEENTH = "minor_thirteenth"   # 小十三度
    MAJOR_THIRTEENTH = "major_thirteenth"   # 大十三度
    MINOR_FOURTEENTH = "minor_fourteenth"   # 小十四度
    MAJOR_FOURTEENTH = "major_fourteenth"   # 大十四度
    PERFECT_FIFTEENTH = "perfect_fifteenth" # 纯十五度

#TODO
# class Interval(str, Enum):
#     # 单音程
#     MINOR_SECOND = ("minor_second", "小二度")
#     MAJOR_SECOND = ("major_second", "大二度")
#     MINOR_THIRD = ("minor_third", "小三度")
#     MAJOR_THIRD = ("major_third", "大三度")
#     PERFECT_FOURTH = ("perfect_fourth", "纯四度")
#     TRITONE = ("tritone", "增四度/减五度")
#     PERFECT_FIFTH = ("perfect_fifth", "纯五度")
#     MINOR_SIXTH = ("minor_sixth", "小六度")
#     MAJOR_SIXTH = ("major_sixth", "大六度")
#     MINOR_SEVENTH = ("minor_seventh", "小七度")
#     MAJOR_SEVENTH = ("major_seventh", "大七度")
#     PERFECT_OCTAVE = ("perfect_octave", "纯八度")
#
#     # 复音程
#     MINOR_NINTH = ("minor_ninth", "小九度")
#     MAJOR_NINTH = ("major_ninth", "大九度")
#     MINOR_TENTH = ("minor_tenth", "小十度")
#     MAJOR_TENTH = ("major_tenth", "大十度")
#     PERFECT_ELEVENTH = ("perfect_eleventh", "纯十一度")
#     AUGMENTED_ELEVENTH = ("augmented_eleventh", "增十一度")
#     PERFECT_TWELFTH = ("perfect_twelfth", "纯十二度")
#     MINOR_THIRTEENTH = ("minor_thirteenth", "小十三度")
#     MAJOR_THIRTEENTH = ("major_thirteenth", "大十三度")
#     MINOR_FOURTEENTH = ("minor_fourteenth", "小十四度")
#     MAJOR_FOURTEENTH = ("major_fourteenth", "大十四度")
#     PERFECT_FIFTEENTH = ("perfect_fifteenth", "纯十五度")
#
#     def __init__(self, value, description):
#         self._value_ = value  # 设置枚举值
#         self.description = description  # 添加描述字段
#
#     def __str__(self):
#         return self.value  # 返回枚举值

class PitchIntervalPair:
    def __init__(self, first: Pitch, second: Pitch) -> None:
        self.first = first
        self.second = second

# 音程模型
class PitchInterval:
    def __init__(self, index:int, interval: Interval, semitones: int, list: List[PitchIntervalPair], count: int) -> None:
        self.index = index
        self.interval = interval
        self.semitones = semitones
        self.list = list
        self.count = count


# 和弦模型
class Chord(enum.Enum):
    # 三和弦
    MAJOR = ("major", "大三和弦", 4, 7)  # 大三度 + 小三度
    MINOR = ("minor", "小三和弦", 3, 7)  # 小三度 + 大三度
    AUGMENTED = ("augmented", "增三和弦", 4, 8)  # 大三度 + 大三度
    DIMINISHED = ("diminished", "减三和弦", 3, 6)  # 小三度 + 小三度

    # 七和弦
    MAJOR_SEVENTH = ("major_seventh", "大七和弦", 4, 7, 11)  # 大三度 + 小三度 + 大三度
    MINOR_SEVENTH = ("minor_seventh", "小七和弦", 3, 7, 10)  # 小三度 + 大三度 + 小三度
    DOMINANT_SEVENTH = ("dominant_seventh", "大小七和弦", 4, 7, 10)  # 大三度 + 小三度 + 小三度
    MINOR_MAJOR_SEVENTH = ("minor_major_seventh", "小大七和弦", 3, 7, 11)  # 小三度 + 小三度 + 小三度
    HALF_DIMINISHED = ("half_diminished", "半减七和弦", 3, 6, 10)  # 小三度 + 小三度 + 大三度
    DIMINISHED_SEVENTH = ("diminished_seventh", "减七和弦", 3, 6, 9)  # 小三度 + 小三度 + 小三度
    AUGMENTED_MAJOR_SEVENTH = ("diminished_seventh", "减七和弦", 4, 8, 11)  # 小三度 + 小三度 + 小三度

    #
    # # 九和弦
    # MAJOR_NINTH = ("major_ninth", "大九和弦", 4, 7, 11, 14)  # 大三度 + 小三度 + 大三度 + 小三度
    # MINOR_NINTH = ("minor_ninth", "小九和弦", 3, 7, 10, 14)  # 小三度 + 大三度 + 小三度 + 大三度
    # DOMINANT_NINTH = ("dominant_ninth", "属九和弦", 4, 7, 10, 14)  # 大三度 + 小三度 + 小三度 + 大三度

    def __init__(self, value, cn_value, *intervals):
        self._value_ = value  # 设置枚举值
        self.cn_value = cn_value  # 设置描述
        self.intervals = intervals  # 设置音程列表

    def __str__(self):
        return self.value  # 返回枚举值


# 和弦模型
class PitchChord:
    def __init__(self, index: int, value: str, cn_value: str, list: List[List], count: int) -> None:
        self.index = index
        self.value = value
        self.cn_value = cn_value
        self.list = list
        self.count = count

















#
# # 音名枚举（A0到C8，覆盖钢琴88个键）
# class PitchName(str, enum.Enum):
#     # 低音区（A0-B0）
#     A0 = "A0"
#     AS0 = "A#0"
#     B0 = "B0"
#
#     # 第一八度
#     C1 = "C1"
#     CS1 = "C#1"
#     D1 = "D1"
#     DS1 = "D#1"
#     E1 = "E1"
#     F1 = "F1"
#     FS1 = "F#1"
#     G1 = "G1"
#     GS1 = "G#1"
#     A1 = "A1"
#     AS1 = "A#1"
#     B1 = "B1"
#
#     # 第二八度
#     C2 = "C2"
#     CS2 = "C#2"
#     D2 = "D2"
#     DS2 = "D#2"
#     E2 = "E2"
#     F2 = "F2"
#     FS2 = "F#2"
#     G2 = "G2"
#     GS2 = "G#2"
#     A2 = "A2"
#     AS2 = "A#2"
#     B2 = "B2"
#
#     # 第三八度
#     C3 = "C3"
#     CS3 = "C#3"
#     D3 = "D3"
#     DS3 = "D#3"
#     E3 = "E3"
#     F3 = "F3"
#     FS3 = "F#3"
#     G3 = "G3"
#     GS3 = "G#3"
#     A3 = "A3"
#     AS3 = "A#3"
#     B3 = "B3"
#
#     # 第四八度（包含中央C）
#     C4 = "C4"
#     CS4 = "C#4"
#     D4 = "D4"
#     DS4 = "D#4"
#     E4 = "E4"
#     F4 = "F4"
#     FS4 = "F#4"
#     G4 = "G4"
#     GS4 = "G#4"
#     A4 = "A4"  # 标准音A4=440Hz
#     AS4 = "A#4"
#     B4 = "B4"
#
#     # 第五八度
#     C5 = "C5"
#     CS5 = "C#5"
#     D5 = "D5"
#     DS5 = "D#5"
#     E5 = "E5"
#     F5 = "F5"
#     FS5 = "F#5"
#     G5 = "G5"
#     GS5 = "G#5"
#     A5 = "A5"
#     AS5 = "A#5"
#     B5 = "B5"
#
#     # 第六八度
#     C6 = "C6"
#     CS6 = "C#6"
#     D6 = "D6"
#     DS6 = "D#6"
#     E6 = "E6"
#     F6 = "F6"
#     FS6 = "F#6"
#     G6 = "G6"
#     GS6 = "G#6"
#     A6 = "A6"
#     AS6 = "A#6"
#     B6 = "B6"
#
#     # 第七八度
#     C7 = "C7"
#     CS7 = "C#7"
#     D7 = "D7"
#     DS7 = "D#7"
#     E7 = "E7"
#     F7 = "F7"
#     FS7 = "F#7"
#     G7 = "G7"
#     GS7 = "G#7"
#     A7 = "A7"
#     AS7 = "A#7"
#     B7 = "B7"
#
#     # 高音区（C8）
#     C8 = "C8"
#

#
# # 和弦类型枚举
# class ChordType(str, enum.Enum):
#     MAJOR = "major"               # 大三和弦
#     MINOR = "minor"               # 小三和弦
#     DIMINISHED = "diminished"     # 减三和弦
#     AUGMENTED = "augmented"       # 增三和弦
#     MAJOR_SEVENTH = "major_seventh"  # 大七和弦
#     MINOR_SEVENTH = "minor_seventh"  # 小七和弦
#     DOMINANT_SEVENTH = "dominant_seventh"  # 属七和弦
#     HALF_DIMINISHED = "half_diminished"   # 半减七和弦
#     DIMINISHED_SEVENTH = "diminished_seventh"  # 减减七和弦
#     MAJOR_NINTH = "major_ninth"   # 大九和弦
#     MINOR_NINTH = "minor_ninth"   # 小九和弦
#     DOMINANT_NINTH = "dominant_ninth"  # 属九和弦
#
# # 音高模型
# # class Pitch(BaseModel):
# #     name: PitchName
# #     file_path: str
# #     frequency: float  # 频率（Hz）
#


#

#
# # 全局常量定义
# PITCH_FILE_MAPPING: Dict[PitchName, str] = {
#     # 这里将在API中动态填充
# }
#

#
# # 预定义的音程列表
# INTERVALS = [
#     # 单音程
#     IntervalModel(
#         name=Interval.MINOR_SECOND,
#         semitones=1,
#         description="小二度",
#         example=[PitchName.C4, PitchName.CS4]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_SECOND,
#         semitones=2,
#         description="大二度",
#         example=[PitchName.C4, PitchName.D4]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_THIRD,
#         semitones=3,
#         description="小三度",
#         example=[PitchName.C4, PitchName.DS4]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_THIRD,
#         semitones=4,
#         description="大三度",
#         example=[PitchName.C4, PitchName.E4]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_FOURTH,
#         semitones=5,
#         description="纯四度",
#         example=[PitchName.C4, PitchName.F4]
#     ),
#     IntervalModel(
#         name=Interval.TRITONE,
#         semitones=6,
#         description="增四度/减五度",
#         example=[PitchName.C4, PitchName.FS4]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_FIFTH,
#         semitones=7,
#         description="纯五度",
#         example=[PitchName.C4, PitchName.G4]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_SIXTH,
#         semitones=8,
#         description="小六度",
#         example=[PitchName.C4, PitchName.GS4]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_SIXTH,
#         semitones=9,
#         description="大六度",
#         example=[PitchName.C4, PitchName.A4]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_SEVENTH,
#         semitones=10,
#         description="小七度",
#         example=[PitchName.C4, PitchName.AS4]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_SEVENTH,
#         semitones=11,
#         description="大七度",
#         example=[PitchName.C4, PitchName.B4]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_OCTAVE,
#         semitones=12,
#         description="纯八度",
#         example=[PitchName.C4, PitchName.C5]
#     ),
#
#     # 复音程
#     IntervalModel(
#         name=Interval.MINOR_NINTH,
#         semitones=13,
#         description="小九度",
#         example=[PitchName.C4, PitchName.CS5]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_NINTH,
#         semitones=14,
#         description="大九度",
#         example=[PitchName.C4, PitchName.D5]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_TENTH,
#         semitones=15,
#         description="小十度",
#         example=[PitchName.C4, PitchName.DS5]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_TENTH,
#         semitones=16,
#         description="大十度",
#         example=[PitchName.C4, PitchName.E5]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_ELEVENTH,
#         semitones=17,
#         description="纯十一度",
#         example=[PitchName.C4, PitchName.F5]
#     ),
#     IntervalModel(
#         name=Interval.AUGMENTED_ELEVENTH,
#         semitones=18,
#         description="增十一度/减十二度",
#         example=[PitchName.C4, PitchName.FS5]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_TWELFTH,
#         semitones=19,
#         description="纯十二度",
#         example=[PitchName.C4, PitchName.G5]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_THIRTEENTH,
#         semitones=20,
#         description="小十三度",
#         example=[PitchName.C4, PitchName.GS5]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_THIRTEENTH,
#         semitones=21,
#         description="大十三度",
#         example=[PitchName.C4, PitchName.A5]
#     ),
#     IntervalModel(
#         name=Interval.MINOR_FOURTEENTH,
#         semitones=22,
#         description="小十四度",
#         example=[PitchName.C4, PitchName.AS5]
#     ),
#     IntervalModel(
#         name=Interval.MAJOR_FOURTEENTH,
#         semitones=23,
#         description="大十四度",
#         example=[PitchName.C4, PitchName.B5]
#     ),
#     IntervalModel(
#         name=Interval.PERFECT_FIFTEENTH,
#         semitones=24,
#         description="纯十五度",
#         example=[PitchName.C4, PitchName.C6]
#     )
# ]
#
# # 预定义的和弦列表
# CHORDS = [
#     # C大调的三和弦
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MAJOR,
#         notes=[PitchName.C4, PitchName.E4, PitchName.G4],
#         description="C大三和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MINOR,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.G4],
#         description="C小三和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.DIMINISHED,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.FS4],
#         description="C减三和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.AUGMENTED,
#         notes=[PitchName.C4, PitchName.E4, PitchName.GS4],
#         description="C增三和弦"
#     ),
#
#     # C大调的七和弦
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MAJOR_SEVENTH,
#         notes=[PitchName.C4, PitchName.E4, PitchName.G4, PitchName.B4],
#         description="C大七和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MINOR_SEVENTH,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.G4, PitchName.AS4],
#         description="C小七和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.DOMINANT_SEVENTH,
#         notes=[PitchName.C4, PitchName.E4, PitchName.G4, PitchName.AS4],
#         description="C属七和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.HALF_DIMINISHED,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.FS4, PitchName.AS4],
#         description="C半减七和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.DIMINISHED_SEVENTH,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.FS4, PitchName.A4],
#         description="C减减七和弦"
#     ),
#
#     # C大调的九和弦
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MAJOR_NINTH,
#         notes=[PitchName.C4, PitchName.E4, PitchName.G4, PitchName.B4, PitchName.D5],
#         description="C大九和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.MINOR_NINTH,
#         notes=[PitchName.C4, PitchName.DS4, PitchName.G4, PitchName.AS4, PitchName.D5],
#         description="C小九和弦"
#     ),
#     Chord(
#         root=PitchName.C4,
#         type=ChordType.DOMINANT_NINTH,
#         notes=[PitchName.C4, PitchName.E4, PitchName.G4, PitchName.AS4, PitchName.D5],
#         description="C属九和弦"
#     ),
#
#     # G大调的主要和弦
#     Chord(
#         root=PitchName.G4,
#         type=ChordType.MAJOR,
#         notes=[PitchName.G4, PitchName.B4, PitchName.D5],
#         description="G大三和弦"
#     ),
#     Chord(
#         root=PitchName.G4,
#         type=ChordType.DOMINANT_SEVENTH,
#         notes=[PitchName.G4, PitchName.B4, PitchName.D5, PitchName.F5],
#         description="G属七和弦"
#     ),
#
#     # F大调的主要和弦
#     Chord(
#         root=PitchName.F4,
#         type=ChordType.MAJOR,
#         notes=[PitchName.F4, PitchName.A4, PitchName.C5],
#         description="F大三和弦"
#     ),
#     Chord(
#         root=PitchName.F4,
#         type=ChordType.MAJOR_SEVENTH,
#         notes=[PitchName.F4, PitchName.A4, PitchName.C5, PitchName.E5],
#         description="F大七和弦"
#     )
# ]