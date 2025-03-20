from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class PitchType(enum.Enum):
    SINGLE_NOTE = "single_note"      # 单音测试
    INTERVAL = "interval"            # 音程测试
    CHORD = "chord"                  # 和弦测试
    MELODY = "melody"                # 旋律测试


class PitchTest(Base):
    __tablename__ = "pitch_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(Enum(PitchType))
    
    # 测试内容
    target_note = Column(String)      # 目标音高（如 "C4", "G4-B4-D5"）
    user_recording = Column(String)    # 用户录音文件路径
    pitch_accuracy = Column(Float)     # 音高准确度（0-100）
    timing_accuracy = Column(Float)    # 节奏准确度（0-100，仅用于旋律测试）
    
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    #user = relationship("User", back_populates="pitch_tests")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(Enum(PitchType))
    
    # 练习数据
    duration = Column(Integer)         # 练习时长（秒）
    notes_practiced = Column(Integer)  # 练习音符数量
    average_accuracy = Column(Float)   # 平均准确度
    
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    # user = relationship("User", back_populates="practice_sessions")