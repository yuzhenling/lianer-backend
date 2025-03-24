# app/api/v1/rhythm_api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.rhythm_service import RhythmService
from app.models.rhythm import *

router = APIRouter(prefix="/api/v1/rhythm", tags=["rhythm"])


@router.post("/generate", response_model=RhythmQuestionResponse)
async def generate_rhythm_question(
        request: RhythmQuestionRequest,
        db: Session = Depends(get_db)
):
    """生成节奏听写题"""
    try:
        rhythm_service = RhythmService()
        response = rhythm_service.generate_question(request)

        # 保存题目到数据库
        question = RhythmQuestion(
            difficulty=request.difficulty,
            time_signature=request.time_signature,
            measures_count=request.measures_count,
            tempo=request.tempo,
            correct_rhythm=response.dict()
        )
        db.add(question)
        db.commit()

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/settings", response_model=dict)
async def get_rhythm_settings():
    """获取节奏听写设置选项"""
    return {
        "difficulties": [d.value for d in RhythmDifficulty],
        "time_signatures": [ts.value for ts in TimeSignature],
        "measures_counts": [4, 6, 8, 10, 12, 16],
        "tempo_range": {
            "min": 40,
            "max": 120,
            "default": 80
        }
    }