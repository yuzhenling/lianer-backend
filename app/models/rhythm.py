# app/models/rhythm.py

from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum, JSON, func

from app.db.database import Base
from app.models.rhythm_settings import TimeSignature, RhythmDifficulty, MeasureCount, Tempo





class RhythmQuestion(Base):
    __tablename__ = "rhythm_questions"

    id = Column(Integer, primary_key=True, index=True)
    difficulty = Column(SQLEnum(RhythmDifficulty))
    time_signature = Column(String)
    measures_count = Column(Integer)
    tempo = Column(Integer)
    correct_rhythm = Column(JSON)  # 存储正确的节奏模式
    created_at = Column(DateTime, server_default=func.now())




