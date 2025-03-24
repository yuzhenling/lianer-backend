# app/models/rhythm.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum, JSON
from app.db.base import Base


class RhythmDifficulty(str, Enum):
    LOW = "low"  # 低难度：主要是四分音符、二分音符
    MEDIUM = "medium"  # 中等：加入八分音符
    HIGH = "high"  # 高难度：加入十六分音符、符点音符


class TimeSignature(str, Enum):
    TWO_FOUR = "2/4"
    THREE_FOUR = "3/4"
    FOUR_FOUR = "4/4"
    THREE_EIGHT = "3/8"
    SIX_EIGHT = "6/8"


class RhythmNote(BaseModel):
    duration: float  # 音符时值：1.0=四分音符，0.5=八分音符，2.0=二分音符
    is_rest: bool = False  # 是否是休止符
    is_dotted: bool = False  # 是否是符点音符
    tied_to_next: bool = False  # 是否有连音线


class RhythmMeasure(BaseModel):
    notes: List[RhythmNote]


class RhythmScore(BaseModel):
    measures: List[RhythmMeasure]
    time_signature: TimeSignature
    tempo: int
    is_correct: bool  # 标记是否是正确答案


class RhythmQuestion(Base):
    __tablename__ = "rhythm_questions"

    id = Column(Integer, primary_key=True, index=True)
    difficulty = Column(SQLEnum(RhythmDifficulty))
    time_signature = Column(String)
    measures_count = Column(Integer)
    tempo = Column(Integer)
    correct_rhythm = Column(JSON)  # 存储正确的节奏模式
    created_at = Column(DateTime, default=datetime.utcnow)


# API请求和响应模型
class RhythmQuestionRequest(BaseModel):
    difficulty: RhythmDifficulty
    time_signature: TimeSignature = TimeSignature.TWO_FOUR
    measures_count: int = Field(ge=4, le=16, default=8)
    tempo: int = Field(ge=40, le=120, default=80)


class RhythmQuestionResponse(BaseModel):
    id: int
    correct_answer: str  # A, B, C 或 D
    options: List[RhythmScore]
    tempo: int
    time_signature: TimeSignature
    measures_count: int
    difficulty: RhythmDifficulty