# app/models/rhythm.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum, JSON, func
from app.db.base import Base
from app.models.rhythmSettings import TimeSignature, RhythmDifficulty, MeasureCount, Tempo


class RhythmNote(BaseModel):
    duration: float  # 音符时值：1.0=四分音符，0.5=八分音符，2.0=二分音符
    is_rest: bool = False  # 是否是休止符
    is_dotted: bool = False  # 是否是符点音符
    tied_to_next: bool = False  # 是否有连音线


class RhythmMeasure(BaseModel):
    notes: List[RhythmNote]


class RhythmScore(BaseModel):
    measures: List[List[RhythmMeasure]]
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
    created_at = Column(DateTime, server_default=func.now())


# API请求和响应模型
class RhythmQuestionRequest(BaseModel):
    difficulty: RhythmDifficulty
    time_signature: TimeSignature = TimeSignature.TWO_FOUR
    measures_count: MeasureCount = MeasureCount.FOUR
    tempo: Tempo = Tempo.EIGHTY


class RhythmQuestionResponse(BaseModel):
    id: int
    correct_answer: str  # A, B, C 或 D
    options: List[RhythmScore]
    tempo: int
    time_signature: TimeSignature
    measures_count: int
    difficulty: RhythmDifficulty