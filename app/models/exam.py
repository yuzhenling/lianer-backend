from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from app.models.pitch import Pitch, PitchIntervalPair
from app.models.pitch_setting import PitchRange

@dataclass
class Question:
    id: int
    pitch: Pitch  # 音高，如 "C4"

@dataclass
class ExamType(Enum):
    SINGLE = ("single", "单音听辨", 20)
    GROUP = ("group", "音组听辨", 20)
    INTERVAL = ("interval", "音程听辨", 20)
    def __init__(self, value, display_value, question_num):
        self._value = value  # 设置枚举值
        self.display_value = display_value  # 设置描述
        self.question_num = question_num  # 设置音程列表

    def __str__(self):
        return self.value  # 返回枚举值


@dataclass
class SinglePitchExam:
    id: int
    user_id: int
    exam_type: str
    question_num: int
    questions: List[Question]
    correct_number: int = 0
    wrong_number: int = 0
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None


@dataclass
class GroupQuestion:
    id: int
    pitches: List[Pitch]  # 音高，如 "C4"

@dataclass
class GroupPitchExam:
    id: int
    user_id: int
    exam_type: str
    question_num: int
    questions: List[GroupQuestion]
    correct_number: int = 0
    wrong_number: int = 0
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None

@dataclass
class IntervalQuestion:
    id: int
    answer_id: int
    answer_name: str
    question: PitchIntervalPair

@dataclass
class PitchIntervalExam:
    id: int
    user_id: int
    exam_type: str
    question_num: int
    questions: List[IntervalQuestion]
    correct_number: int = 0
    wrong_number: int = 0
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
