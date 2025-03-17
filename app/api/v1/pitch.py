 from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
from datetime import datetime

from app.services.audio_processing import AudioProcessor
from app.models.pitch import PitchTest, PitchType, PracticeSession
from app.models.user import User
from app.core.config import settings
from app.api.v1.auth import get_current_user, get_db

router = APIRouter()
audio_processor = AudioProcessor()


class PitchTestCreate(BaseModel):
    type: PitchType
    target_note: str


class PitchTestResponse(BaseModel):
    id: int
    type: PitchType
    target_note: str
    pitch_accuracy: float
    timing_accuracy: float
    created_at: datetime

    class Config:
        orm_mode = True


@router.post("/pitch-test", response_model=PitchTestResponse)
async def create_pitch_test(
    test_data: PitchTestCreate,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的音高测试"""
    # 保存音频文件
    file_path = os.path.join(settings.AUDIO_UPLOAD_DIR, f"{current_user.id}_{datetime.now().timestamp()}.wav")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # 加载并分析音频
    audio, sr = audio_processor.load_audio(file_path)
    
    # 根据测试类型进行分析
    if test_data.type in [PitchType.SINGLE_NOTE, PitchType.INTERVAL, PitchType.CHORD]:
        target_notes = test_data.target_note.split("-")
        pitch_accuracy, timing_accuracy = audio_processor.analyze_melody(audio, target_notes)
    else:  # 旋律测试
        target_notes = test_data.target_note.split("-")
        pitch_accuracy, timing_accuracy = audio_processor.analyze_melody(audio, target_notes)
    
    # 创建测试记录
    pitch_test = PitchTest(
        user_id=current_user.id,
        type=test_data.type,
        target_note=test_data.target_note,
        user_recording=file_path,
        pitch_accuracy=pitch_accuracy,
        timing_accuracy=timing_accuracy
    )
    
    db.add(pitch_test)
    
    # 更新用户统计
    current_user.pitch_test_count += 1
    
    db.commit()
    db.refresh(pitch_test)
    
    return pitch_test


@router.get("/pitch-tests/history", response_model=List[PitchTestResponse])
async def get_pitch_test_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的音高测试历史"""
    tests = db.query(PitchTest)\
        .filter(PitchTest.user_id == current_user.id)\
        .order_by(PitchTest.created_at.desc())\
        .limit(50)\
        .all()
    return tests


class PracticeSessionCreate(BaseModel):
    type: PitchType
    duration: int
    notes_practiced: int
    average_accuracy: float


@router.post("/practice-session")
async def create_practice_session(
    session_data: PracticeSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录练习会话"""
    session = PracticeSession(
        user_id=current_user.id,
        type=session_data.type,
        duration=session_data.duration,
        notes_practiced=session_data.notes_practiced,
        average_accuracy=session_data.average_accuracy
    )
    
    db.add(session)
    
    # 更新用户统计
    current_user.total_practice_time += session_data.duration // 60  # 转换为分钟
    
    db.commit()
    
    return {"status": "success"}